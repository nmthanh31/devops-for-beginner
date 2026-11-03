from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from redis.exceptions import RedisError

from kubernetes_alert_gateway.api.dependencies import get_dedup_store
from kubernetes_alert_gateway.clients.telegram import TelegramClient
from kubernetes_alert_gateway.main import app
from kubernetes_alert_gateway.services.dedup import DedupStore

client = TestClient(app)

AUTH_HEADERS = {
    "Authorization": "Bearer test-webhook-token",
}


def create_webhook_payload(
    alerts: list[dict[str, object]],
    status: str = "firing",
) -> dict[str, object]:
    """Tạo phần bao ngoài giống payload Alertmanager thật cho các API test."""

    return {
        "version": "4",
        "groupKey": "{}",
        "status": status,
        "receiver": "telegram",
        "alerts": alerts,
    }


@pytest.fixture
def fake_telegram(monkeypatch):
    fake_send_message = AsyncMock()
    monkeypatch.setattr(
        TelegramClient,
        "send_message",
        fake_send_message,
    )
    return fake_send_message


@pytest.fixture(autouse=True)
def fake_dedup_store():
    store = AsyncMock(spec=DedupStore)
    store.claim.return_value = True

    app.dependency_overrides[get_dedup_store] = lambda: store

    yield store

    app.dependency_overrides.pop(get_dedup_store, None)


@pytest.fixture(autouse=True)
def test_environment(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123456")
    monkeypatch.setenv("WEBHOOK_TOKEN", "test-webhook-token")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("DEDUP_TTL_SECONDS", "300")


def test_receives_two_alerts(
    fake_telegram,
    fake_dedup_store,
):
    payload = create_webhook_payload(
        alerts=[
            {
                "status": "firing",
                "labels": {
                    "alertname": "HighCPU",
                    "severity": "warning",
                },
                "annotations": {
                    "summary": "CPU usage is high",
                },
            },
            {
                "status": "resolved",
                "labels": {
                    "alertname": "HighMemory",
                    "severity": "critical",
                },
                "annotations": {
                    "summary": "Memory usage returned to normal",
                },
            },
        ],
    )

    response = client.post(
        "/api/v1/webhooks/alertmanager",
        json=payload,
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 202
    assert response.json()["status"] == "processed"
    assert response.json()["amount_alerts"] == 2
    assert response.json()["sent_alerts"] == 2
    assert response.json()["duplicate_alerts"] == 0
    assert fake_telegram.await_count == 2
    assert fake_dedup_store.claim.await_count == 2

    claimed_keys = [
        call.args[0]
        for call in fake_dedup_store.claim.await_args_list
    ]
    assert all(key.startswith("alertmanager:") for key in claimed_keys)

    sent_texts = [call.kwargs["text"] for call in fake_telegram.await_args_list]
    assert "HighCPU" in sent_texts[0]
    assert "HighMemory" in sent_texts[1]


def test_duplicate_alert_is_not_sent(
    fake_telegram,
    fake_dedup_store,
):
    fake_dedup_store.claim.side_effect = [True, False]
    payload = create_webhook_payload(
        alerts=[
            {
                "status": "firing",
                "labels": {
                    "alertname": "HighCPU",
                },
            },
            {
                "status": "firing",
                "labels": {
                    "alertname": "HighCPU",
                },
            },
        ],
    )

    response = client.post(
        "/api/v1/webhooks/alertmanager",
        json=payload,
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 202
    assert response.json()["amount_alerts"] == 2
    assert response.json()["sent_alerts"] == 1
    assert response.json()["duplicate_alerts"] == 1
    assert fake_dedup_store.claim.await_count == 2
    assert fake_telegram.await_count == 1

    first_key = fake_dedup_store.claim.await_args_list[0].args[0]
    second_key = fake_dedup_store.claim.await_args_list[1].args[0]
    assert first_key == second_key


def test_missing_alerts_field():
    payload = {
        "version": "4",
        "groupKey": "{}",
        "status": "firing",
        "receiver": "telegram",
    }

    response = client.post(
        "/api/v1/webhooks/alertmanager",
        json=payload,
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 422


def test_alert_with_wrong_status():
    payload = create_webhook_payload(
        alerts=[
            {
                "status": "pending",
                "labels": {},
                "annotations": {},
            }
        ],
    )

    response = client.post(
        "/api/v1/webhooks/alertmanager",
        json=payload,
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 422


def test_missing_labels_annotation(fake_telegram):
    payload = create_webhook_payload(
        alerts=[
            {
                "status": "firing",
            }
        ],
    )

    response = client.post(
        "/api/v1/webhooks/alertmanager",
        json=payload,
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 202
    assert response.json()["amount_alerts"] == 1
    assert response.json()["sent_alerts"] == 1
    assert response.json()["duplicate_alerts"] == 0
    assert fake_telegram.await_count == 1


def test_telegram_failure_return_502(
    fake_telegram,
    fake_dedup_store,
):
    fake_telegram.side_effect = RuntimeError("fake Telegram failure")
    payload = create_webhook_payload(
        alerts=[
            {
                "status": "firing",
                "labels": {
                    "alertname": "HighCPU",
                    "severity": "warning",
                },
                "annotations": {
                    "summary": "CPU usage is high",
                },
            }
        ],
    )

    response = client.post(
        "/api/v1/webhooks/alertmanager",
        json=payload,
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Telegram delivery failed"
    assert fake_telegram.await_count == 1
    fake_dedup_store.claim.assert_awaited_once()
    claimed_key = fake_dedup_store.claim.await_args.args[0]
    assert claimed_key.startswith("alertmanager:")
    fake_dedup_store.release.assert_awaited_once_with(claimed_key)


def test_missing_webhook_token_return_401(fake_telegram):
    payload = create_webhook_payload(
        alerts=[
            {
                "status": "firing",
            }
        ],
    )

    response = client.post(
        "/api/v1/webhooks/alertmanager",
        json=payload,
    )

    assert response.status_code == 401
    assert response.json()["detail"] == ("Invalid or missing webhook token")
    assert fake_telegram.await_count == 0


def test_wrong_webhook_token_return_401(fake_telegram):
    payload = create_webhook_payload(
        alerts=[
            {
                "status": "firing",
            }
        ],
    )

    response = client.post(
        "/api/v1/webhooks/alertmanager",
        json=payload,
        headers={
            "Authorization": "Bearer wrong-token",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == ("Invalid or missing webhook token")
    assert fake_telegram.await_count == 0


def test_redis_claim_failure_returns_503(fake_telegram, fake_dedup_store):
    fake_dedup_store.claim.side_effect = RedisError("fake Redis failure")
    payload = create_webhook_payload(
        alerts=[
            {
                "status": "firing",
                "labels": {
                    "alertname": "HighCPU",
                },
            }
        ],
    )

    response = client.post(
        "/api/v1/webhooks/alertmanager",
        json=payload,
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Dedup service unavailable"

    fake_dedup_store.claim.assert_awaited_once()
    claimed_key = fake_dedup_store.claim.await_args.args[0]
    assert claimed_key.startswith("alertmanager:")

    assert fake_telegram.await_count == 0


def test_redis_release_failure_returns_503(fake_telegram, fake_dedup_store):
    fake_dedup_store.claim.return_value = True
    fake_telegram.side_effect = RuntimeError("fake Telegram failure")

    fake_dedup_store.release.side_effect = RedisError("fake Redis release failure")

    payload = create_webhook_payload(
        alerts=[
            {
                "status": "firing",
                "labels": {
                    "alertname": "HighCPU",
                },
            }
        ],
    )

    response = client.post(
        "/api/v1/webhooks/alertmanager", json=payload, headers=AUTH_HEADERS
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Telegram delivery failed and dedup cleanup failed"
    )

    fake_dedup_store.claim.assert_awaited_once()
    claimed_key = fake_dedup_store.claim.await_args.args[0]
    assert claimed_key.startswith("alertmanager:")

    assert fake_telegram.await_count == 1

    fake_dedup_store.release.assert_awaited_once_with(claimed_key)
