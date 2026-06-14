"""API router — TaskExecution (reporting + query)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import ExecutionOut, ExecutionReport
from app.services import ExecutionService, TaskService, AgentService

router = APIRouter(prefix="/api/tasks/{task_id}/executions", tags=["executions"])


@router.post("", response_model=ExecutionOut, status_code=201)
async def report_execution(task_id: int, body: ExecutionReport,
                           db: AsyncSession = Depends(get_db)):
    """Agent reports execution result for a task."""
    # Verify task exists
    task_svc = TaskService(db)
    task = await task_svc.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")

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


@router.get("", response_model=list[ExecutionOut])
async def list_executions(
    task_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    exec_svc = ExecutionService(db)
    records = await exec_svc.get_executions(task_id, limit=limit, offset=offset)
    return [ExecutionOut(**r.__dict__) for r in records]


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
