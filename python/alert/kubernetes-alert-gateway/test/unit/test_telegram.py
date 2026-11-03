import asyncio
import json

import httpx
import pytest

from kubernetes_alert_gateway.clients.telegram import TelegramClient
from kubernetes_alert_gateway.core.config import Settings


def test_send_message_builds_telegram_requests():
    captured = {}

    def handler(request):
        captured["method"] = request.method
        captured["url"] = str(request.url)
        captured["body"] = json.loads(request.content)

        return httpx.Response(status_code=200, json={"ok": True})

    async def run_test():
        transport = httpx.MockTransport(handler=handler)
        settings = Settings(
            telegram_bot_token="test-token",
            telegram_chat_id="123456",
            webhook_token="test-webhook-token",
            redis_url="redis://localhost:6379",
        )
        async with httpx.AsyncClient(transport=transport, timeout=10) as http_client:
            telegram_client = TelegramClient(settings=settings, http_client=http_client)
            await telegram_client.send_message(text="CPU usage is high")

    asyncio.run(run_test())

    assert captured["method"] == "POST"
    assert captured["url"].endswith("/bottest-token/sendMessage")
    assert captured["body"] == {
        "chat_id": "123456",
        "text": "CPU usage is high",
    }


def test_send_message_raises_when_telegram_returns_not_ok():
    def handler(request):
        return httpx.Response(
            status_code=200,
            json={"ok": False, "description": "Bad Requests: chat not found"},
        )

    async def run_test():
        transport = httpx.MockTransport(handler=handler)
        settings = Settings(
            telegram_bot_token="test-token",
            telegram_chat_id="123456",
            webhook_token="test-webhook-token",
            redis_url="redis://localhost:6379",
        )
        async with httpx.AsyncClient(transport=transport, timeout=10) as http_client:
            telegram_client = TelegramClient(settings=settings, http_client=http_client)

            await telegram_client.send_message(text="Test message")

    with pytest.raises(
        RuntimeError,
        match="Bad Requests: chat not found",
    ):
        asyncio.run(run_test())


def test_send_message_raises_on_http_error():
    def handler(request):
        return httpx.Response(
            status_code=500,
            json={"ok": False},
        )

    async def run_test():
        transport = httpx.MockTransport(handler=handler)
        settings = Settings(
            telegram_bot_token="test-token",
            telegram_chat_id="123456",
            webhook_token="test-webhook-token",
            redis_url="redis://localhost:6379",
        )

        async with httpx.AsyncClient(transport=transport, timeout=10) as http_client:
            telegram_client = TelegramClient(settings=settings, http_client=http_client)

            await telegram_client.send_message(text="Test message")

    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(run_test())
