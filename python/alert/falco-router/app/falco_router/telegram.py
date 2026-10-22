"""Minimal Telegram Bot API client for formatted Falco alerts."""

import os

import httpx


class TelegramDeliveryError(RuntimeError):
    """Raised when Telegram cannot accept an alert; message contains no secrets."""


async def send_message(message: str) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise TelegramDeliveryError("Telegram credentials are not configured")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "disable_web_page_preview": True}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        # Do not include the original exception: its URL can contain the bot token.
        raise TelegramDeliveryError("Telegram request failed") from exc

    if not isinstance(result, dict) or result.get("ok") is not True:
        raise TelegramDeliveryError("Telegram rejected the message")
