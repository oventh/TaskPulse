"""Pydantic schemas — Notifications & Alerts."""

from datetime import datetime

from pydantic import BaseModel, Field


# ── Notification Channel ──────────────────────────────────────────────

class NotificationChannelCreate(BaseModel):
    name: str = Field(..., max_length=128)
    channel_type: str = Field(..., pattern=r"^(feishu_cli|email|webhook)$")
    config: str = Field(..., description="JSON 配置字符串")


class NotificationChannelUpdate(BaseModel):
    name: str | None = Field(None, max_length=128)
    config: str | None = None
    enabled: bool | None = None


class NotificationChannelOut(BaseModel):
    id: int
    name: str
    channel_type: str
    config: str
    enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Alert Rule ────────────────────────────────────────────────────────

class AlertRuleCreate(BaseModel):
    task_id: int
    channel_id: int
    alert_type: str = Field(default="missed_run", pattern=r"^(missed_run|failure)$")


class AlertRuleOut(BaseModel):
    id: int
    task_id: int
    channel_id: int
    channel_name: str = ""
    alert_type: str
    enabled: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Alert ─────────────────────────────────────────────────────────────

class AlertOut(BaseModel):
    id: int
    task_id: int | None = None
    task_name: str = ""
    alert_type: str
    message: str
    status: str
    acknowledged_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertAcknowledge(BaseModel):
    pass
