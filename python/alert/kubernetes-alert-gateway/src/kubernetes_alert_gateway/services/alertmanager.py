import logging
from dataclasses import dataclass

import httpx
from redis.exceptions import RedisError

from kubernetes_alert_gateway.clients.telegram import TelegramClient
from kubernetes_alert_gateway.domain.models import NormalizedAlert
from kubernetes_alert_gateway.mappers.alertmanager import map_alertmanager_payload
from kubernetes_alert_gateway.schemas.alertmanager import AlertmanagerPayload
from kubernetes_alert_gateway.services.dedup import (
    DedupStore,
    build_dedup_key,
)
from kubernetes_alert_gateway.services.formatter import format_alert

logger = logging.getLogger(__name__)


class DedupUnavailableError(Exception):
    """Redis không thể kiểm tra hoặc tạo dedup key."""


class TelegramDeliveryError(Exception):
    """Telegram không nhận được alert nhưng dedup key đã được dọn sạch."""


class DedupCleanupError(Exception):
    """Telegram gửi lỗi và Redis cũng không thể xóa dedup key."""


@dataclass(frozen=True)
class AlertProcessingResult:
    """Kết quả nghiệp vụ trả về sau khi xử lý toàn bộ payload."""

    amount_alerts: int
    sent_alerts: int
    duplicate_alerts: int


def build_alert_messages(alerts: list[NormalizedAlert]) -> list[str]:
    """Format mỗi alert trong payload thành đúng một Telegram message."""

    messages: list[str] = []

    for alert in alerts:
        messages.append(format_alert(alert=alert))

    return messages


async def process_alerts(
    payload: AlertmanagerPayload,
    telegram_client: TelegramClient,
    dedup_store: DedupStore,
) -> AlertProcessingResult:
    """Dedup và gửi từng alert; không chứa khái niệm HTTP/FastAPI."""
    alerts = map_alertmanager_payload(payload=payload)
    messages = build_alert_messages(alerts=alerts)
    sent_alerts = 0
    duplicate_alerts = 0

    # Không log toàn bộ payload vì labels/annotations có thể chứa dữ liệu
    # nội bộ. Số lượng alert là đủ để theo dõi request ở mức vận hành.
    logger.info(
        "alertmanager_webhook_received alert_count=%s",
        len(alerts),
    )

    for alert, message in zip(
        alerts,
        messages,
        strict=True,
    ):
        # Các giá trị dự phòng bảo đảm logging không lỗi khi field bị thiếu.
        alertname = alert.alert_name
        namespace = alert.namespace or "unknown"
        fingerprint = alert.fingerprint
        dedup_key = build_dedup_key(alert=alert)

        
        try:
            # True: key mới và được phép gửi. False: alert trùng trong TTL.
            is_new = await dedup_store.claim(dedup_key)
        except RedisError as exc:
            logger.error(
                (
                    "dedup_claim_failed "
                    "alertname=%s namespace=%s "
                    "fingerprint=%s status=%s error_type=%s"
                ),
                alertname,
                namespace,
                fingerprint,
                alert.status,
                type(exc).__name__,
            )
            # Service phát exception nghiệp vụ; route chịu trách nhiệm
            # chuyển nó thành HTTP 503.
            raise DedupUnavailableError from exc

        if not is_new:
            duplicate_alerts += 1
            logger.info(
                (
                    "alert_duplicate_skipped "
                    "alertname=%s namespace=%s "
                    "fingerprint=%s status=%s"
                ),
                alertname,
                namespace,
                fingerprint,
                alert.status,
            )
            continue

        try:
            await telegram_client.send_message(text=message)
            sent_alerts += 1
            logger.info(
                ("alert_sent alertname=%s namespace=%s fingerprint=%s status=%s"),
                alertname,
                namespace,
                fingerprint,
                alert.status,
            )
        except (httpx.HTTPError, RuntimeError) as exc:
            # Không ghi raw exception HTTPX vì request URL của Telegram có thể
            # chứa bot token. Chỉ log loại lỗi và metadata an toàn.
            logger.error(
                (
                    "telegram_delivery_failed "
                    "alertname=%s namespace=%s "
                    "fingerprint=%s status=%s error_type=%s"
                ),
                alertname,
                namespace,
                fingerprint,
                alert.status,
                type(exc).__name__,
            )

            try:
                    # Telegram chưa nhận alert nên xóa key để lần retry sau
                    # có thể claim và gửi lại.
                await dedup_store.release(dedup_key)
            except RedisError as redis_exc:
                logger.error(
                    (
                        "dedup_release_failed "
                        "alertname=%s namespace=%s "
                        "fingerprint=%s status=%s error_type=%s"
                    ),
                    alertname,
                    namespace,
                    fingerprint,
                    alert.status,
                    type(redis_exc).__name__,
                )
                raise DedupCleanupError from redis_exc

            raise TelegramDeliveryError from exc

    return AlertProcessingResult(
        amount_alerts=len(alerts),
        sent_alerts=sent_alerts,
        duplicate_alerts=duplicate_alerts,
    )
