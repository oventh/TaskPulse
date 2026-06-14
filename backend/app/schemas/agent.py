"""Pydantic schemas — Agent."""

from datetime import datetime

from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    name: str = Field(..., max_length=128)
    description: str = Field(default="")


class AgentUpdate(BaseModel):
    name: str | None = Field(None, max_length=128)
    description: str | None = None
    status: str | None = None  # active / inactive


class AgentOut(BaseModel):
    id: int
    name: str
    description: str
    api_key: str
    status: str
    last_heartbeat_at: datetime | None = None
    task_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentHeartbeat(BaseModel):
    pass


# ── Batch registration (AI agent self-registers with tasks) ───────

class TaskRegistrationItem(BaseModel):
    """A single task an agent wants to register."""
    name: str = Field(..., max_length=256)
    description: str = Field(default="")
    cron_expression: str = Field(..., max_length=64)
    grace_period: int = Field(default=300, ge=0)


class AgentBatchRegister(BaseModel):
    """AI agent sends this to register itself + all its tasks in one call."""
    name: str = Field(..., max_length=128)
    description: str = Field(default="")
    tasks: list[TaskRegistrationItem] = Field(default_factory=list)


class AgentBatchRegisterResult(BaseModel):
    """Response for batch registration."""
    agent: AgentOut
    tasks_created: int
