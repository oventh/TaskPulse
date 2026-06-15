"""Agent business logic."""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Agent, ScheduledTask


class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, name: str, description: str = "") -> Agent:
        agent = Agent(name=name, description=description)
        self.db.add(agent)
        await self.db.flush()
        await self.db.refresh(agent)
        return agent

    async def get(self, agent_id: int) -> Agent | None:
        return await self.db.get(Agent, agent_id)

    async def get_by_api_key(self, api_key: str) -> Agent | None:
        stmt = select(Agent).where(Agent.api_key == api_key)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Agent]:
        stmt = select(Agent).order_by(Agent.id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, agent_id: int, **kwargs) -> Agent | None:
        agent = await self.get(agent_id)
        if agent is None:
            return None
        for k, v in kwargs.items():
            if v is not None and hasattr(agent, k):
                setattr(agent, k, v)
        await self.db.flush()
        await self.db.refresh(agent)
        return agent

    async def heartbeat(self, agent_id: int) -> Agent | None:
        from datetime import datetime
        agent = await self.get(agent_id)
        if agent:
            agent.last_heartbeat_at = datetime.utcnow()
            await self.db.flush()
            await self.db.refresh(agent)
        return agent

    async def get_task_count(self, agent_id: int) -> int:
        stmt = select(func.count(ScheduledTask.id)).where(ScheduledTask.agent_id == agent_id)
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def delete(self, agent_id: int) -> bool:
        agent = await self.get(agent_id)
        if agent is None:
            return False
        await self.db.delete(agent)
        await self.db.flush()
        return True
