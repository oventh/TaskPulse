"""Model registry — all models are imported here so Alembic can discover them."""

from app.models.agent import Agent  # noqa: F401
from app.models.task import ScheduledTask  # noqa: F401
from app.models.execution import TaskExecution  # noqa: F401
from app.models.notification import Alert, AlertRule, NotificationChannel  # noqa: F401
from app.models.system_config import SystemConfig  # noqa: F401
from app.models.user import User  # noqa: F401

__all__ = ["Agent", "ScheduledTask", "TaskExecution", "NotificationChannel",
           "AlertRule", "Alert", "SystemConfig", "User"]
