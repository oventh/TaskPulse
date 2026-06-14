"""API router — Task management."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import TaskCreate, TaskOut, TaskUpdate
from app.services import TaskService, AgentService

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("", response_model=TaskOut, status_code=201)
async def create_task(body: TaskCreate, agent_id: int, db: AsyncSession = Depends(get_db)):
    """Create a task for a specific agent. Pass agent_id as query param."""
    svc = TaskService(db)
    agent_svc = AgentService(db)
    agent = await agent_svc.get(agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    task = await svc.create(
        agent_id=agent_id,
        name=body.name,
        cron_expression=body.cron_expression,
        description=body.description,
        grace_period=body.grace_period,
    )
    return TaskOut(**{**task.__dict__, "agent_name": agent.name})


@router.get("", response_model=list[TaskOut])
async def list_tasks(agent_id: int | None = None, db: AsyncSession = Depends(get_db)):
    """List all tasks, optionally filtered by agent_id."""
    svc = TaskService(db)
    agent_svc = AgentService(db)
    if agent_id:
        tasks = await svc.list_by_agent(agent_id)
    else:
        tasks = await svc.list_all()
    result = []
    for t in tasks:
        agent = await agent_svc.get(t.agent_id)
        result.append(TaskOut(**{**t.__dict__, "agent_name": agent.name if agent else ""}))
    return result


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    svc = TaskService(db)
    agent_svc = AgentService(db)
    task = await svc.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    agent = await agent_svc.get(task.agent_id)
    return TaskOut(**{**task.__dict__, "agent_name": agent.name if agent else ""})


@router.put("/{task_id}", response_model=TaskOut)
async def update_task(task_id: int, body: TaskUpdate, db: AsyncSession = Depends(get_db)):
    svc = TaskService(db)
    agent_svc = AgentService(db)
    task = await svc.update(task_id, **body.model_dump(exclude_none=True))
    if not task:
        raise HTTPException(404, "Task not found")
    agent = await agent_svc.get(task.agent_id)
    return TaskOut(**{**task.__dict__, "agent_name": agent.name if agent else ""})


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    svc = TaskService(db)
    ok = await svc.delete(task_id)
    if not ok:
        raise HTTPException(404, "Task not found")
