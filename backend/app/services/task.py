"""ScheduledTask business logic."""

from datetime import datetime

from croniter import croniter
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ScheduledTask, Agent


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, agent_id: int, name: str, cron_expression: str,
                     description: str = "", grace_period: int = 300) -> ScheduledTask:
        now = datetime.utcnow()
        next_run = self._calc_next_run(cron_expression, now)
        task = ScheduledTask(
            agent_id=agent_id,
            name=name,
            description=description,
            cron_expression=cron_expression,
            grace_period=grace_period,
            next_run_at=next_run,
        )
        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def get(self, task_id: int) -> ScheduledTask | None:
        return await self.db.get(ScheduledTask, task_id)

    async def list_by_agent(self, agent_id: int) -> list[ScheduledTask]:
        stmt = select(ScheduledTask).where(ScheduledTask.agent_id == agent_id).order_by(ScheduledTask.id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_all(self, status: str | None = None) -> list[ScheduledTask]:
        stmt = select(ScheduledTask)
        if status:
            stmt = stmt.where(ScheduledTask.status == status)
        stmt = stmt.order_by(ScheduledTask.id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, task_id: int, **kwargs) -> ScheduledTask | None:
        task = await self.get(task_id)
        if task is None:
            return None
        for k, v in kwargs.items():
            if v is not None and hasattr(task, k):
                setattr(task, k, v)
        # Recalculate next_run if cron changed
        if kwargs.get("cron_expression"):
            task.next_run_at = self._calc_next_run(task.cron_expression, datetime.utcnow())
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def delete(self, task_id: int) -> bool:
        task = await self.get(task_id)
        if task is None:
            return False
        await self.db.delete(task)
        await self.db.flush()
        return True

    async def mark_run(self, task_id: int, success: bool) -> ScheduledTask | None:
        """Mark that a task just ran: update last_run, total_count, next_run."""
        task = await self.get(task_id)
        if task is None:
            return None
        now = datetime.utcnow()
        task.last_run_at = now
        task.last_run_result = "success" if success else "failed"
        task.total_run_count = (task.total_run_count or 0) + 1
        task.next_run_at = self._calc_next_run(task.cron_expression, now)
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def get_overdue_tasks(self, grace_seconds: int) -> list[ScheduledTask]:
        """Find active tasks whose next_run_at + grace_period is in the past."""
        now = datetime.utcnow()
        stmt = select(ScheduledTask).where(
            ScheduledTask.status == "active",
            ScheduledTask.next_run_at.isnot(None),
            ScheduledTask.next_run_at + func.make_interval(0, 0, 0, 0, 0, 0, grace_seconds) < now,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    def _calc_next_run(cron_expression: str, base: datetime | None = None) -> datetime | None:
        try:
            cron = croniter(cron_expression, base or datetime.utcnow())
            return cron.get_next(datetime)
        except (ValueError, KeyError):
            return None
