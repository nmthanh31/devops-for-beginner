import asyncio
from typing import Literal
from unittest.mock import AsyncMock

from kubernetes_alert_gateway.domain.models import NormalizedAlert
from kubernetes_alert_gateway.services.dedup import DedupStore, build_dedup_key


def create_alert(
    source: Literal["alertmanager", "falco"] = "alertmanager",
    fingerprint: str = "abc123",
) -> NormalizedAlert:
    return NormalizedAlert(
        status="firing",
        source=source,
        alert_name="HighCPU",
        fingerprint=fingerprint,
    )


def test_create_dedup_key():
    alert = create_alert(fingerprint="abc123")

    result = build_dedup_key(alert=alert)

    assert result == "alertmanager:abc123"


def test_source_is_part_of_dedup_key():
    alertmanager_alert = create_alert(source="alertmanager")
    falco_alert = create_alert(source="falco")

    assert build_dedup_key(alertmanager_alert) == "alertmanager:abc123"
    assert build_dedup_key(falco_alert) == "falco:abc123"


def test_claim_returns_true_for_new_key():
    redis_client = AsyncMock()
    redis_client.set.return_value = True
    store = DedupStore(redis_client=redis_client, ttl_seconds=300)

    result = asyncio.run(store.claim("alertmanager:abc123"))

    assert result is True
    redis_client.set.assert_awaited_once_with(
        name="alertmanager:abc123",
        value="1",
        ex=300,
        nx=True,
    )


def test_claim_returns_false_for_existing_key():
    redis_client = AsyncMock()
    redis_client.set.return_value = None
    store = DedupStore(redis_client=redis_client, ttl_seconds=300)

    result = asyncio.run(store.claim("alertmanager:abc123"))

    assert result is False
    redis_client.set.assert_awaited_once_with(
        name="alertmanager:abc123",
        value="1",
        ex=300,
        nx=True,
    )


def test_release_deletes_key():
    redis_client = AsyncMock()
    store = DedupStore(
        redis_client=redis_client,
        ttl_seconds=300,
    )

    asyncio.run(store.release("alertmanager:abc123"))

    redis_client.delete.assert_awaited_once_with("alertmanager:abc123")
