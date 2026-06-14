"""TaskExecution business logic."""

from datetime import datetime

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TaskExecution, ScheduledTask, Agent


class ExecutionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def start_execution(self, task_id: int, agent_id: int) -> TaskExecution:
        """Agent 开始执行任务时创建一个 running 记录."""
        exec_record = TaskExecution(task_id=task_id, agent_id=agent_id, status="running")
        self.db.add(exec_record)
        await self.db.flush()
        await self.db.refresh(exec_record)
        return exec_record

    async def report_result(self, task_id: int, agent_id: int,
                            status: str, finished_at: datetime | None = None,
                            duration_ms: int | None = None,
                            result: str | None = None,
                            log: str | None = None,
                            error_message: str | None = None) -> TaskExecution | None:
        """Agent 汇报执行结果：创建一条完成记录并更新任务的 last_run 信息。"""
        now = finished_at or datetime.utcnow()

        exec_record = TaskExecution(
            task_id=task_id,
            agent_id=agent_id,
            status=status,
            started_at=now,
            finished_at=now,
            duration_ms=duration_ms,
            result=result,
            log=log,
            error_message=error_message,
        )
        self.db.add(exec_record)
        await self.db.flush()
        await self.db.refresh(exec_record)
        return exec_record

    async def get_executions(self, task_id: int, limit: int = 50, offset: int = 0) -> list[TaskExecution]:
        stmt = (
            select(TaskExecution)
            .where(TaskExecution.task_id == task_id)
            .order_by(desc(TaskExecution.id))
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_execution(self, execution_id: int) -> TaskExecution | None:
        return await self.db.get(TaskExecution, execution_id)

    async def get_recent_executions(self, limit: int = 100) -> list[TaskExecution]:
        stmt = (
            select(TaskExecution)
            .order_by(desc(TaskExecution.id))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
