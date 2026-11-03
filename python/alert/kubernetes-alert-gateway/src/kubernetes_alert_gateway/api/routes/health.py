from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from redis.exceptions import RedisError

from kubernetes_alert_gateway.api.dependencies import get_redis_client
from kubernetes_alert_gateway.schemas.health import LivenessResponse, ReadinessResponse

health_router = APIRouter()


@health_router.get("/health/live", response_model=LivenessResponse)
async def liveness() -> LivenessResponse:
    return LivenessResponse()


@health_router.get("/health/ready", response_model=ReadinessResponse)
async def readiness(
    redis_client: Annotated[Redis, Depends(get_redis_client)],
) -> ReadinessResponse:
    try:
        await redis_client.ping()
    except RedisError as exc:
        raise HTTPException(status_code=503, detail="Redis unavailable") from exc
    return ReadinessResponse()
