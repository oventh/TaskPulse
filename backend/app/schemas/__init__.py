"""Pydantic schema registry."""

from app.schemas.agent import AgentBatchRegister, AgentBatchRegisterResult, AgentCreate, AgentHeartbeat, AgentOut, AgentUpdate  # noqa: F401
from app.schemas.auth import LoginRequest, TokenResponse, UserInfo, UserOut  # noqa: F401
from app.schemas.execution import ExecutionOut, ExecutionReport  # noqa: F401
from app.schemas.notification import (  # noqa: F401
    AlertAcknowledge,
    AlertOut,
    AlertRuleCreate,
    AlertRuleOut,
    NotificationChannelCreate,
    NotificationChannelOut,
    NotificationChannelUpdate,
)
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate  # noqa: F401

__all__ = [
    "AgentCreate", "AgentUpdate", "AgentOut", "AgentHeartbeat",
    "TaskCreate", "TaskUpdate", "TaskOut",
    "ExecutionReport", "ExecutionOut",
    "NotificationChannelCreate", "NotificationChannelUpdate", "NotificationChannelOut",
    "AlertRuleCreate", "AlertRuleOut",
    "AlertOut", "AlertAcknowledge",
]
