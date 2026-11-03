import secrets
from collections.abc import AsyncGenerator
from typing import Annotated

import httpx
from fastapi import Header, HTTPException, Request
from redis.asyncio import Redis

from kubernetes_alert_gateway.clients.telegram import TelegramClient
from kubernetes_alert_gateway.core.config import Settings
from kubernetes_alert_gateway.services.dedup import DedupStore


async def get_telegram_client() -> AsyncGenerator[TelegramClient]:
    settings = Settings()

    async with httpx.AsyncClient(timeout=10) as http_client:
        telegram_client = TelegramClient(settings=settings, http_client=http_client)

        yield telegram_client


def verify_webhook_token(
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    """Kiểm tra Bearer token trong header Authorization của webhook."""

    # FastAPI lấy header `Authorization` và truyền vào tham số `authorization`.
    # Ví dụ: `Authorization: Bearer abc123` trở thành chuỗi "Bearer abc123".
    # Nếu request không gửi header này thì giá trị là None.

    # Đọc token đúng từ biến môi trường WEBHOOK_TOKEN (hoặc file .env).
    settings = Settings()

    # Chuẩn bị cùng một response lỗi cho mọi trường hợp xác thực thất bại.
    # Không nói rõ token thiếu hay sai để tránh tiết lộ thông tin không cần thiết.
    unauthorized = HTTPException(
        status_code=401,
        detail="Invalid or missing webhook token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Không có header Authorization thì dừng ngay; route phía sau không được chạy.
    if authorization is None:
        raise unauthorized

    # Tách "Bearer abc123" thành ba phần:
    # scheme="Bearer", separator=" ", token="abc123".
    # Nếu không có dấu cách thì separator và token sẽ là chuỗi rỗng.
    scheme, separator, token = authorization.partition(" ")

    # Header hợp lệ phải dùng Bearer, có dấu cách phân tách và token phải khớp.
    # compare_digest() được dùng cho dữ liệu bí mật để tránh so sánh theo kiểu
    # dừng ngay tại ký tự sai đầu tiên.
    if (
        scheme.lower() != "bearer"
        or separator == ""
        or not secrets.compare_digest(
            token,
            settings.webhook_token,
        )
    ):
        raise unauthorized

    # Nếu không có exception nào được raise, token hợp lệ và hàm tự trả về None.


def get_dedup_store(request: Request) -> DedupStore:
    return request.app.state.dedup_store


def get_redis_client(request: Request) -> Redis:
    return request.app.state.redis_client
