import asyncio
from unittest.mock import AsyncMock

import pytest
from redis.exceptions import RedisError

from kubernetes_alert_gateway.clients.telegram import TelegramClient
from kubernetes_alert_gateway.domain.models import NormalizedAlert
from kubernetes_alert_gateway.schemas.alertmanager import (
    AlertItem,
    AlertmanagerPayload,
)
from kubernetes_alert_gateway.services.alertmanager import (
    DedupCleanupError,
    DedupUnavailableError,
    TelegramDeliveryError,
    build_alert_messages,
    process_alerts,
)
from kubernetes_alert_gateway.services.dedup import DedupStore


def create_payload() -> AlertmanagerPayload:
    """Tạo payload nhỏ dùng chung cho các test xử lý nghiệp vụ."""

    return AlertmanagerPayload(
        version="4",
        groupKey='{}:{alertname="HighCPU"}',
        status="firing",
        receiver="telegram",
        alerts=[
            AlertItem(
                status="firing",
                labels={
                    "alertname": "HighCPU",
                    "severity": "warning",
                    "namespace": "production",
                },
                annotations={"summary": "CPU usage is high"},
            )
        ]
    )


def test_builds_one_message_for_each_alert():
    alerts = [
        NormalizedAlert(
            status="firing",
            source="alertmanager",
            alert_name="HighCPU",
            severity="warning",
            fingerprint="fingerprint-1",
            namespace="production",
            summary="CPU usage is high",
        ),
        NormalizedAlert(
            status="resolved",
            source="alertmanager",
            alert_name="HighMemory",
            severity="critical",
            fingerprint="fingerprint-2",
            namespace="staging",
            summary="Memory usage returned to normal",
        ),
    ]

    messages = build_alert_messages(alerts)

    assert len(messages) == 2
    assert "HighCPU" in messages[0]
    assert "CPU usage is high" in messages[0]
    assert "HighMemory" in messages[1]
    assert "Memory usage returned to normal" in messages[1]
    assert messages[0] != messages[1]


def test_process_alerts_sends_new_alert():
    telegram_client = AsyncMock(spec=TelegramClient)
    dedup_store = AsyncMock(spec=DedupStore)
    dedup_store.claim.return_value = True

    result = asyncio.run(
        process_alerts(
            payload=create_payload(),
            telegram_client=telegram_client,
            dedup_store=dedup_store,
        )
    )

    assert result.amount_alerts == 1
    assert result.sent_alerts == 1
    assert result.duplicate_alerts == 0
    dedup_store.claim.assert_awaited_once()
    claimed_key = dedup_store.claim.await_args.args[0]
    assert claimed_key.startswith("alertmanager:")
    assert telegram_client.send_message.await_count == 1


def test_process_alerts_skips_duplicate():
    telegram_client = AsyncMock(spec=TelegramClient)
    dedup_store = AsyncMock(spec=DedupStore)
    dedup_store.claim.return_value = False

    result = asyncio.run(
        process_alerts(
            payload=create_payload(),
            telegram_client=telegram_client,
            dedup_store=dedup_store,
        )
    )

    assert result.amount_alerts == 1
    assert result.sent_alerts == 0
    assert result.duplicate_alerts == 1
    dedup_store.claim.assert_awaited_once()
    assert telegram_client.send_message.await_count == 0


def test_process_alerts_raises_when_dedup_is_unavailable():
    telegram_client = AsyncMock(spec=TelegramClient)
    dedup_store = AsyncMock(spec=DedupStore)
    dedup_store.claim.side_effect = RedisError("fake Redis failure")

    with pytest.raises(DedupUnavailableError):
        asyncio.run(
            process_alerts(
                payload=create_payload(),
                telegram_client=telegram_client,
                dedup_store=dedup_store,
            )
        )

    assert telegram_client.send_message.await_count == 0


def test_process_alerts_releases_key_when_telegram_fails():
    telegram_client = AsyncMock(spec=TelegramClient)
    telegram_client.send_message.side_effect = RuntimeError("fake Telegram failure")
    dedup_store = AsyncMock(spec=DedupStore)
    dedup_store.claim.return_value = True

    with pytest.raises(TelegramDeliveryError):
        asyncio.run(
            process_alerts(
                payload=create_payload(),
                telegram_client=telegram_client,
                dedup_store=dedup_store,
            )
        )

    claimed_key = dedup_store.claim.await_args.args[0]
    dedup_store.release.assert_awaited_once_with(claimed_key)


def test_process_alerts_raises_when_dedup_cleanup_fails():
    telegram_client = AsyncMock(spec=TelegramClient)
    telegram_client.send_message.side_effect = RuntimeError("fake Telegram failure")
    dedup_store = AsyncMock(spec=DedupStore)
    dedup_store.claim.return_value = True
    dedup_store.release.side_effect = RedisError("fake Redis release failure")

    with pytest.raises(DedupCleanupError):
        asyncio.run(
            process_alerts(
                payload=create_payload(),
                telegram_client=telegram_client,
                dedup_store=dedup_store,
            )
        )

    claimed_key = dedup_store.claim.await_args.args[0]
    dedup_store.release.assert_awaited_once_with(claimed_key)
