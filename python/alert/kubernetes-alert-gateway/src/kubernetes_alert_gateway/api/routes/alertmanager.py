from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from kubernetes_alert_gateway.api.dependencies import (
    get_dedup_store,
    get_telegram_client,
    verify_webhook_token,
)
from kubernetes_alert_gateway.clients.telegram import TelegramClient
from kubernetes_alert_gateway.schemas.alertmanager import (
    AlertmanagerPayload,
    AlertmanagerResponse,
)
from kubernetes_alert_gateway.services.alertmanager import (
    DedupCleanupError,
    DedupUnavailableError,
    TelegramDeliveryError,
    process_alerts,
)
from kubernetes_alert_gateway.services.dedup import DedupStore

alertmanager_router = APIRouter()


@alertmanager_router.post(
    "/api/v1/webhooks/alertmanager",
    status_code=202,
    dependencies=[Depends(verify_webhook_token)],
    response_model=AlertmanagerResponse,
)
async def receive_alerts(
    payload: AlertmanagerPayload,
    telegram_client: Annotated[
        TelegramClient,
        Depends(get_telegram_client),
    ],
    dedup_store: Annotated[
        DedupStore,
        Depends(get_dedup_store),
    ],
) -> AlertmanagerResponse:
    try:
        # Route chỉ điều phối HTTP. Dedup, Telegram và logging nằm trong
        # service để có thể tái sử dụng mà không phụ thuộc FastAPI.
        result = await process_alerts(
            payload=payload,
            telegram_client=telegram_client,
            dedup_store=dedup_store,
        )
    except DedupUnavailableError as exc:
        # Redis không kiểm tra được dedup key nên yêu cầu client thử lại.
        raise HTTPException(
            status_code=503,
            detail="Dedup service unavailable",
        ) from exc
    except DedupCleanupError as exc:
        # Telegram đã lỗi và Redis cũng không xóa được key vừa claim.
        raise HTTPException(
            status_code=503,
            detail=("Telegram delivery failed and dedup cleanup failed"),
        ) from exc
    except TelegramDeliveryError as exc:
        # Redis cleanup đã thành công (hoặc alert không có fingerprint), nhưng
        # Telegram không nhận được message.
        raise HTTPException(
            status_code=502,
            detail="Telegram delivery failed",
        ) from exc

    return AlertmanagerResponse(
        amount_alerts=result.amount_alerts,
        sent_alerts=result.sent_alerts,
        duplicate_alerts=result.duplicate_alerts,
    )
