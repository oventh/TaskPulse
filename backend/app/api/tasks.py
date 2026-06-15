"""API router — Task management."""

import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import TaskCreate, TaskOut, TaskUpdate
from app.services import TaskService, AgentService
from app.models import ScheduledTask

router = APIRouter(prefix="/api/tasks", tags=["tags"])


def _task_to_out(task, agent_name: str = "") -> dict:
    """Convert task model to TaskOut dict, handling tags JSON deserialization."""
    data = {**task.__dict__}
    try:
        data["tags"] = json.loads(data.get("tags", "[]"))
    except (json.JSONDecodeError, TypeError):
        data["tags"] = []
    data["agent_name"] = agent_name
    return data


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
    # Store tags
    if body.tags:
        task.tags = json.dumps(body.tags, ensure_ascii=False)
        await db.flush()
        await db.refresh(task)
    return TaskOut(**_task_to_out(task, agent.name))


@router.get("", response_model=list[TaskOut])
async def list_tasks(
    agent_id: int | None = Query(None),
    q: str | None = Query(None, description="关键词搜索（任务名称）"),
    tags: str | None = Query(None, description="标签筛选，逗号分隔"),
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all tasks, with optional search and filters."""
    svc = TaskService(db)
    agent_svc = AgentService(db)

    # Build query
    stmt = select(ScheduledTask)
    if agent_id:
        stmt = stmt.where(ScheduledTask.agent_id == agent_id)
    if status:
        stmt = stmt.where(ScheduledTask.status == status)
    if q:
        stmt = stmt.where(ScheduledTask.name.like(f"%{q}%"))
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        for tag in tag_list:
            stmt = stmt.where(ScheduledTask.tags.like(f'%"{tag}"%'))

    stmt = stmt.order_by(ScheduledTask.id)
    result = await db.execute(stmt)
    tasks = list(result.scalars().all())

    output = []
    for t in tasks:
        agent = await agent_svc.get(t.agent_id)
        output.append(TaskOut(**_task_to_out(t, agent.name if agent else "")))
    return output


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    svc = TaskService(db)
    agent_svc = AgentService(db)
    task = await svc.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    agent = await agent_svc.get(task.agent_id)
    return TaskOut(**_task_to_out(task, agent.name if agent else ""))


@router.put("/{task_id}", response_model=TaskOut)
async def update_task(task_id: int, body: TaskUpdate, db: AsyncSession = Depends(get_db)):
    svc = TaskService(db)
    agent_svc = AgentService(db)

    # Handle tags separately (JSON serialization)
    update_data = body.model_dump(exclude_none=True)
    tags_list = update_data.pop("tags", None)

    task = await svc.update(task_id, **update_data)
    if not task:
        raise HTTPException(404, "Task not found")

    if tags_list is not None:
        task.tags = json.dumps(tags_list, ensure_ascii=False)
        await db.flush()
        await db.refresh(task)

    agent = await agent_svc.get(task.agent_id)
    return TaskOut(**_task_to_out(task, agent.name if agent else ""))


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    svc = TaskService(db)
    ok = await svc.delete(task_id)
    if not ok:
        raise HTTPException(404, "Task not found")
