"""SQLAlchemy models — ScheduledTask."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False, comment="任务名称")
    description: Mapped[str] = mapped_column(Text, default="", comment="任务描述")
    cron_expression: Mapped[str] = mapped_column(String(64), nullable=False, comment="Cron 表达式, e.g. */5 * * * *")
    grace_period: Mapped[int] = mapped_column(Integer, default=300, comment="容忍秒数, 超时未执行则告警")
    status: Mapped[str] = mapped_column(String(32), default="active", comment="active / paused / stopped")
    tags: Mapped[str | None] = mapped_column(Text, nullable=True, comment="标签 JSON 数组, e.g. [\"数据同步\",\"重要\"]")

    # 冗余字段方便查询
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="最近一次执行时间")
    last_run_result: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="最近一次执行结果 success/failed")
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="预计下次执行时间")
    total_run_count: Mapped[int] = mapped_column(Integer, default=0, comment="累计执行次数")

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    agent = relationship("Agent", back_populates="tasks")
    executions = relationship("TaskExecution", back_populates="task", cascade="all, delete-orphan")
    alert_rules = relationship("AlertRule", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ScheduledTask {self.name}>"
