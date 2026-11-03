from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    telegram_bot_token: str
    telegram_chat_id: str
    webhook_token: str
    redis_url: str
    dedup_ttl_seconds: int = 300

    # Đã sửa: SettingsConfigDict phải được import ở trên mới dùng được.
    # model_config nói cho Pydantic Settings nơi lấy cấu hình.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Đã sửa: chưa tạo Settings() ngay khi import file.
# Hai giá trị này là bắt buộc; tạo Settings() ở cấp module sẽ làm app/test
# lỗi lập tức nếu máy chưa có file .env hoặc biến môi trường tương ứng.
# Sẽ khởi tạo Settings khi phần gửi Telegram thực sự cần cấu hình.
