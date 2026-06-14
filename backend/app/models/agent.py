"""SQLAlchemy models — Agent."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _gen_api_key() -> str:
    return f"tp_{uuid.uuid4().hex}"


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, comment="Agent 名称")
    description: Mapped[str] = mapped_column(Text, default="", comment="描述")
    api_key: Mapped[str] = mapped_column(String(128), unique=True, default=_gen_api_key, comment="API Key")
    status: Mapped[str] = mapped_column(String(32), default="active", comment="active / inactive")
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="最后心跳时间")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    tasks = relationship("ScheduledTask", back_populates="agent")

    def __repr__(self) -> str:
        return f"<Agent {self.name}>"
