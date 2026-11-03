from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from kubernetes_alert_gateway.api.routes.alertmanager import (
    alertmanager_router,
)
from kubernetes_alert_gateway.api.routes.health import health_router
from kubernetes_alert_gateway.core.config import Settings
from kubernetes_alert_gateway.core.logging import configure_logging
from kubernetes_alert_gateway.services.dedup import DedupStore


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Đọc cấu hình một lần khi ứng dụng khởi động thay vì đọc lại cho từng
    # request cần sử dụng Redis.
    settings = Settings()

    # Redis client tự quản lý connection pool. Client này được chia sẻ cho
    # tất cả request trong suốt vòng đời của ứng dụng.
    redis_client = Redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )

    try:
        # Fail fast: nếu Redis không kết nối được thì app không nhận request
        # trong trạng thái thiếu chức năng dedup.
        await redis_client.ping()

        # Lưu DedupStore vào app.state để dependency có thể lấy ra mà không
        # phải tạo Redis client mới cho từng request.
        app.state.dedup_store = DedupStore(
            redis_client=redis_client,
            ttl_seconds=settings.dedup_ttl_seconds,
        )

        app.state.redis_client = redis_client

        # Code trước yield chạy lúc startup; FastAPI phục vụ request trong
        # thời gian tạm dừng tại yield.
        yield
    finally:
        # Code sau yield chạy khi shutdown, bảo đảm connection pool được đóng.
        await redis_client.aclose()


# Cấu hình logger trước khi FastAPI bắt đầu nhận request.
configure_logging()

app = FastAPI(
    title="Kubernetes Alert Gateway",
    description="Gateway tiếp nhận và gửi cảnh báo Kubernetes",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(alertmanager_router)
