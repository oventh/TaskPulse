"""SQLAlchemy models — NotificationChannel & AlertRule & AlertHistory."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class NotificationChannel(Base):
    """用户绑定的通知渠道"""
    __tablename__ = "notification_channels"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="渠道名称, e.g. 我的飞书")
    channel_type: Mapped[str] = mapped_column(String(32), nullable=False, comment="feishu_cli / email / webhook")
    config: Mapped[str] = mapped_column(Text, nullable=False, comment="JSON 配置")
    enabled: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    alert_rules = relationship("AlertRule", back_populates="channel", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<NotificationChannel {self.name} ({self.channel_type})>"


class AlertRule(Base):
    """告警规则：哪些任务触发哪些通知渠道"""
    __tablename__ = "alert_rules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("scheduled_tasks.id", ondelete="CASCADE"), nullable=False)
    channel_id: Mapped[int] = mapped_column(ForeignKey("notification_channels.id", ondelete="CASCADE"), nullable=False)
    alert_type: Mapped[str] = mapped_column(String(32), default="missed_run", comment="missed_run / failure")
    enabled: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    task = relationship("ScheduledTask", back_populates="alert_rules")
    channel = relationship("NotificationChannel", back_populates="alert_rules")

    def __repr__(self) -> str:
        return f"<AlertRule task={self.task_id} → channel={self.channel_id}>"


class Alert(Base):
    """告警历史"""
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("scheduled_tasks.id", ondelete="SET NULL"), nullable=True)
    alert_type: Mapped[str] = mapped_column(String(32), nullable=False, comment="missed_run / failure / timeout")
    message: Mapped[str] = mapped_column(Text, nullable=False, comment="告警内容")
    status: Mapped[str] = mapped_column(String(32), default="pending", comment="pending / acknowledged / resolved")
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="确认时间")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<Alert #{self.id} type={self.alert_type} status={self.status}>"
