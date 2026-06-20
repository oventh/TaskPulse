"""API router — TaskExecution (reporting + query)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import ExecutionOut, ExecutionReport
from app.services import ExecutionService, TaskService, AgentService
from app.models import TaskExecution

router = APIRouter(prefix="/api/tasks/{task_id}/executions", tags=["executions"])


class PaginatedExecutions(BaseModel):
    items: list[ExecutionOut]
    total: int
    page: int
    page_size: int


@router.post("", response_model=ExecutionOut, status_code=201)
async def report_execution(task_id: int, body: ExecutionReport,
                           db: AsyncSession = Depends(get_db)):
    """Agent reports execution result for a task."""
    # Verify task exists
    task_svc = TaskService(db)
    task = await task_svc.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")

    # Verify agent exists and is active
    agent_svc = AgentService(db)
    agent = await agent_svc.get(task.agent_id)
    if not agent:
        raise HTTPException(410, "Agent已被删除，请重新注册")
    if agent.status != "active":
        raise HTTPException(403, "Agent已停用，无法汇报")

    exec_svc = ExecutionService(db)
    record = await exec_svc.report_result(
        task_id=task_id,
        agent_id=task.agent_id,
        status=body.status,
        finished_at=body.finished_at,
        duration_ms=body.duration_ms,
        result=body.result,
        log=body.log,
        error_message=body.error_message,
    )

    # Update task's last_run info
    await task_svc.mark_run(task_id, success=(body.status == "success"))
    await db.commit()
    return ExecutionOut(**record.__dict__)


@router.get("", response_model=PaginatedExecutions)
async def list_executions(
    task_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    exec_svc = ExecutionService(db)
    offset = (page - 1) * page_size
    records = await exec_svc.get_executions(task_id, limit=page_size, offset=offset)

    # Get total count
    count_stmt = select(func.count()).select_from(TaskExecution).where(TaskExecution.task_id == task_id)
    total = (await db.execute(count_stmt)).scalar() or 0

    return PaginatedExecutions(
        items=[ExecutionOut(**r.__dict__) for r in records],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/recent", response_model=list[ExecutionOut])
async def recent_executions(
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """Get recent executions across all tasks (for dashboard)."""
    exec_svc = ExecutionService(db)
    records = await exec_svc.get_recent_executions(limit=limit)
    return [ExecutionOut(**r.__dict__) for r in records]


@router.get("/{execution_id}", response_model=ExecutionOut)
async def get_execution(execution_id: int, db: AsyncSession = Depends(get_db)):
    exec_svc = ExecutionService(db)
    record = await exec_svc.get_execution(execution_id)
    if not record:
        raise HTTPException(404, "Execution not found")
    return ExecutionOut(**record.__dict__)
