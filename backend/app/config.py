"""Application configuration via environment variables."""

import urllib.parse

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database (internal network)
    DB_HOST: str = "192.168.8.160"
    DB_PORT: int = 3306
    DB_USER: str = "dbuser"
    DB_PASSWORD: str = "Tata@1234"
    DB_NAME: str = "taskpulse"

    # App
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True

    # Secret
    SECRET_KEY: str = "change-me-in-production"

    # Scheduler
    SCHEDULER_CHECK_INTERVAL: int = 60  # seconds
    TASK_GRACE_PERIOD: int = 300  # seconds — how long after expected start before alerting

    # Notifications
    FEISHU_WEBHOOK_URL: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "taskpulse@example.com"

    @property
    def DATABASE_URL(self) -> str:
        pwd = urllib.parse.quote_plus(self.DB_PASSWORD)
        return f"mysql+aiomysql://{self.DB_USER}:{pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    @property
    def DATABASE_URL_SYNC(self) -> str:
        pwd = urllib.parse.quote_plus(self.DB_PASSWORD)
        return f"mysql+pymysql://{self.DB_USER}:{pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    model_config = {"env_prefix": "TASKPULSE_", "env_file": ".env"}


settings = Settings()
