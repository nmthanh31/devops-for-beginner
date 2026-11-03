import asyncio
import os
from uuid import uuid4

import pytest
from redis.asyncio import Redis

from kubernetes_alert_gateway.services.dedup import DedupStore


@pytest.mark.integration
def test_claim_release_with_real_redis():
    async def run_test():
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_client = Redis.from_url(
            redis_url,
            decode_responses=True,
        )
        store = DedupStore(redis_client=redis_client, ttl_seconds=300)
        key = f"test:dedup:{uuid4()}"
        try:
            first_claim = await store.claim(key=key)
            assert first_claim is True

            second_claim = await store.claim(key=key)
            assert second_claim is False

            await store.release(key)

            third_claim = await store.claim(key=key)
            assert third_claim is True
        finally:
            await redis_client.delete(key)
            await redis_client.aclose()

    asyncio.run(run_test())
