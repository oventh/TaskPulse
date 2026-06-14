"""SQLAlchemy models — SystemConfig (key-value store for system settings)."""

from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SystemConfig(Base):
    """System-level configuration stored as key-value pairs."""
    __tablename__ = "system_config"

    key: Mapped[str] = mapped_column(String(128), primary_key=True, comment="配置键名")
    value: Mapped[str] = mapped_column(Text, nullable=False, comment="配置值 (JSON)")
    description: Mapped[str] = mapped_column(String(256), default="", comment="描述")
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<SystemConfig {self.key}={self.value}>"
