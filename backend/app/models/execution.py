"""SQLAlchemy models — TaskExecution."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TaskExecution(Base):
    __tablename__ = "task_executions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("scheduled_tasks.id", ondelete="CASCADE"), nullable=False)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="running", comment="running / success / failed")
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="开始时间")
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="结束时间")
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="耗时（毫秒）")
    result: Mapped[str | None] = mapped_column(Text, nullable=True, comment="执行结果摘要 (JSON)")
    log: Mapped[str | None] = mapped_column(Text, nullable=True, comment="执行日志")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True, comment="错误信息")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    task = relationship("ScheduledTask", back_populates="executions")
    agent = relationship("Agent")

    def __repr__(self) -> str:
        return f"<TaskExecution #{self.id} task={self.task_id} status={self.status}>"
