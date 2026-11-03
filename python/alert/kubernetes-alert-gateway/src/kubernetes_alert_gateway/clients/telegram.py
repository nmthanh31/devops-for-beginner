import httpx

from kubernetes_alert_gateway.core.config import Settings


class TelegramClient:
    def __init__(self, settings: Settings, http_client: httpx.AsyncClient) -> None:
        self.settings = settings
        self.http_client = http_client

    async def send_message(self, text: str) -> None:
        url = f"https://api.telegram.org/bot{self.settings.telegram_bot_token}/sendMessage"
        chat_id = self.settings.telegram_chat_id

        payload = {"chat_id": chat_id, "text": text}

        response = await self.http_client.post(url=url, json=payload)

        response.raise_for_status()

        result = response.json()
        if not result.get("ok"):
            description = result.get("description", "Telegram gửi tin nhắn thất bại")
            raise RuntimeError(description)
