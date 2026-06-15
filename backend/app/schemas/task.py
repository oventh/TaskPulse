"""Pydantic schemas — ScheduledTask."""

from datetime import datetime

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    name: str = Field(..., max_length=256)
    description: str = Field(default="")
    cron_expression: str = Field(..., max_length=64)
    grace_period: int = Field(default=300, ge=0)
    tags: list[str] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    name: str | None = Field(None, max_length=256)
    description: str | None = None
    cron_expression: str | None = None
    grace_period: int | None = None
    status: str | None = None  # active / paused / stopped
    tags: list[str] | None = None


class TaskOut(BaseModel):
    id: int
    agent_id: int
    agent_name: str = ""
    name: str
    description: str
    cron_expression: str
    grace_period: int
    status: str
    tags: list[str] = Field(default_factory=list)
    last_run_at: datetime | None = None
    last_run_result: str | None = None
    next_run_at: datetime | None = None
    total_run_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
