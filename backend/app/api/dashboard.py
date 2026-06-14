"""API router — Dashboard overview."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Agent, Alert, ScheduledTask, TaskExecution

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


class DashboardSummary(BaseModel):
    total_agents: int
    active_agents: int
    total_tasks: int
    active_tasks: int
    total_executions: int
    recent_executions_ok: int
    recent_executions_failed: int
    pending_alerts: int


class DashboardTaskItem(BaseModel):
    id: int
    agent_name: str
    name: str
    cron_expression: str
    status: str
    last_run_at: datetime | None = None
    last_run_result: str | None = None
    next_run_at: datetime | None = None
    total_run_count: int = 0


@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(db: AsyncSession = Depends(get_db)):
    # Agents
    total_agents = (await db.execute(select(func.count(Agent.id)))).scalar() or 0
    active_agents = (
        await db.execute(select(func.count(Agent.id)).where(Agent.status == "active"))
    ).scalar() or 0

    # Tasks
    total_tasks = (await db.execute(select(func.count(ScheduledTask.id)))).scalar() or 0
    active_tasks = (
        await db.execute(
            select(func.count(ScheduledTask.id)).where(ScheduledTask.status == "active")
        )
    ).scalar() or 0

    # Executions (last 24h)
    since = datetime.utcnow() - timedelta(hours=24)
    total_execs = (
        await db.execute(
            select(func.count(TaskExecution.id)).where(TaskExecution.created_at >= since)
        )
    ).scalar() or 0
    ok_execs = (
        await db.execute(
            select(func.count(TaskExecution.id)).where(
                TaskExecution.created_at >= since, TaskExecution.status == "success"
            )
        )
    ).scalar() or 0
    failed_execs = (
        await db.execute(
            select(func.count(TaskExecution.id)).where(
                TaskExecution.created_at >= since, TaskExecution.status == "failed"
            )
        )
    ).scalar() or 0

    # Alerts
    pending_alerts = (
        await db.execute(
            select(func.count(Alert.id)).where(Alert.status == "pending")
        )
    ).scalar() or 0

    return DashboardSummary(
        total_agents=total_agents,
        active_agents=active_agents,
        total_tasks=total_tasks,
        active_tasks=active_tasks,
        total_executions=total_execs,
        recent_executions_ok=ok_execs,
        recent_executions_failed=failed_execs,
        pending_alerts=pending_alerts,
    )


@router.get("/tasks", response_model=list[DashboardTaskItem])
async def dashboard_tasks(db: AsyncSession = Depends(get_db)):
    """Return all tasks with agent name for the unified view."""
    stmt = select(ScheduledTask).order_by(ScheduledTask.id)
    tasks = (await db.execute(stmt)).scalars().all()
    result = []
    for t in tasks:
        agent = await db.get(Agent, t.agent_id)
        result.append(DashboardTaskItem(
            id=t.id,
            agent_name=agent.name if agent else "",
            name=t.name,
            cron_expression=t.cron_expression,
            status=t.status,
            last_run_at=t.last_run_at,
            last_run_result=t.last_run_result,
            next_run_at=t.next_run_at,
            total_run_count=t.total_run_count or 0,
        ))
    return result
