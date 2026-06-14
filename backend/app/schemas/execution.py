"""Pydantic schemas — TaskExecution."""

from datetime import datetime

from pydantic import BaseModel, Field


class ExecutionReport(BaseModel):
    """Agent 汇报执行结果"""
    status: str = Field(..., pattern=r"^(success|failed)$", description="success 或 failed")
    finished_at: datetime | None = None
    duration_ms: int | None = None
    result: str | None = Field(None, description="执行结果摘要 (JSON)")
    log: str | None = Field(None, description="执行日志文本")
    error_message: str | None = None


class ExecutionOut(BaseModel):
    id: int
    task_id: int
    agent_id: int
    status: str
    started_at: datetime
    finished_at: datetime | None = None
    duration_ms: int | None = None
    result: str | None = None
    log: str | None = None
    error_message: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
