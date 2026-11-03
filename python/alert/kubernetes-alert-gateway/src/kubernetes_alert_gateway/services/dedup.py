from redis.asyncio import Redis

from kubernetes_alert_gateway.domain.models import NormalizedAlert


class DedupStore:
    def __init__(
        self,
        redis_client: Redis,
        ttl_seconds: int,
    ) -> None:
        self.redis_client = redis_client
        self.ttl_seconds = ttl_seconds

    async def claim(self, key: str) -> bool:
        result = await self.redis_client.set(
            name=key,
            value="1",
            ex=self.ttl_seconds,
            nx=True,
        )
        return result is True

    async def release(self, key: str) -> None:
        await self.redis_client.delete(key)


def build_dedup_key(alert: NormalizedAlert) -> str:
    return f"{alert.source}:{alert.fingerprint}"
