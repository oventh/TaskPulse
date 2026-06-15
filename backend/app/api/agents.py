"""API router — Agent management."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import AgentBatchRegister, AgentBatchRegisterResult, AgentCreate, AgentHeartbeat, AgentOut, AgentUpdate
from app.services import AgentService, TaskService

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.post("", response_model=AgentOut, status_code=201)
async def register_agent(body: AgentCreate, db: AsyncSession = Depends(get_db)):
    svc = AgentService(db)
    agent = await svc.create(name=body.name, description=body.description)
    task_count = await svc.get_task_count(agent.id)
    return AgentOut(**{**agent.__dict__, "task_count": task_count})


@router.get("", response_model=list[AgentOut])
async def list_agents(db: AsyncSession = Depends(get_db)):
    svc = AgentService(db)
    agents = await svc.list_all()
    result = []
    for a in agents:
        cnt = await svc.get_task_count(a.id)
        result.append(AgentOut(**{**a.__dict__, "task_count": cnt}))
    return result


@router.get("/{agent_id}", response_model=AgentOut)
async def get_agent(agent_id: int, db: AsyncSession = Depends(get_db)):
    svc = AgentService(db)
    agent = await svc.get(agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    cnt = await svc.get_task_count(agent.id)
    return AgentOut(**{**agent.__dict__, "task_count": cnt})


@router.put("/{agent_id}", response_model=AgentOut)
async def update_agent(agent_id: int, body: AgentUpdate, db: AsyncSession = Depends(get_db)):
    svc = AgentService(db)
    agent = await svc.update(agent_id, **body.model_dump(exclude_none=True))
    if not agent:
        raise HTTPException(404, "Agent not found")
    cnt = await svc.get_task_count(agent.id)
    return AgentOut(**{**agent.__dict__, "task_count": cnt})


@router.post("/{agent_id}/heartbeat", response_model=AgentOut)
async def heartbeat(agent_id: int, body: AgentHeartbeat, db: AsyncSession = Depends(get_db)):
    svc = AgentService(db)
    agent = await svc.heartbeat(agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    cnt = await svc.get_task_count(agent.id)
    return AgentOut(**{**agent.__dict__, "task_count": cnt})


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: int, db: AsyncSession = Depends(get_db)):
    svc = AgentService(db)
    agent = await svc.get(agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    # Delete all tasks first, then the agent (cascade)
    await svc.delete(agent_id)
    await db.commit()


# ── Batch registration: AI agent self-registers with all its tasks ─────

@router.post("/register-with-tasks", response_model=AgentBatchRegisterResult, status_code=201)
async def register_agent_with_tasks(body: AgentBatchRegister, db: AsyncSession = Depends(get_db)):
    """AI Agent 一次性注册自己 + 所有定时任务。"""
    agent_svc = AgentService(db)
    task_svc = TaskService(db)

    agent = await agent_svc.create(name=body.name, description=body.description)
    tasks_created = 0
    for t in body.tasks:
        await task_svc.create(
            agent_id=agent.id,
            name=t.name,
            cron_expression=t.cron_expression,
            description=t.description,
            grace_period=t.grace_period,
        )
        tasks_created += 1

    await db.commit()
    task_count = await agent_svc.get_task_count(agent.id)
    return AgentBatchRegisterResult(
        agent=AgentOut(**{**agent.__dict__, "task_count": task_count}),
        tasks_created=tasks_created,
    )
