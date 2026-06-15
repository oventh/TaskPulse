"""Scheduler — periodic check for overdue tasks."""

import asyncio
import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session_factory
from app.models import ScheduledTask, Alert, AlertRule, NotificationChannel
from app.utils import fmt_bj

logger = logging.getLogger("taskpulse.scheduler")


class SchedulerService:
    """Background checker that scans for overdue tasks and triggers alerts."""

    def __init__(self):
        self._running = False

    async def start(self):
        self._running = True
        logger.info("Scheduler started (interval=%ss)", settings.SCHEDULER_CHECK_INTERVAL)
        while self._running:
            try:
                await self._check_overdue()
            except Exception as exc:
                logger.exception("Scheduler check error: %s", exc)
            await asyncio.sleep(settings.SCHEDULER_CHECK_INTERVAL)

    async def stop(self):
        self._running = False
        logger.info("Scheduler stopped")

    async def _check_overdue(self):
        """Find active tasks past their next_run_at + grace_period."""
        async with async_session_factory() as db:
            now = datetime.utcnow()
            stmt = select(ScheduledTask).where(
                ScheduledTask.status == "active",
                ScheduledTask.next_run_at.isnot(None),
                ScheduledTask.next_run_at < now,
            )
            result = await db.execute(stmt)
            tasks = list(result.scalars().all())

            for task in tasks:
                grace_end = task.next_run_at.timestamp() + task.grace_period
                if now.timestamp() <= grace_end:
                    continue  # still within grace window

                # Check if we already alerted recently for this task
                recent = select(Alert).where(
                    Alert.task_id == task.id,
                    Alert.alert_type == "missed_run",
                    Alert.status == "pending",
                )
                existing = (await db.execute(recent)).scalar_one_or_none()
                if existing:
                    continue  # already has pending alert

                alert = Alert(
                    task_id=task.id,
                    alert_type="missed_run",
                    message=(
                        f"任务 [{task.name}](ID={task.id}) 超过预定时间未执行。\n"
                        f"预期执行时间: {fmt_bj(task.next_run_at)}\n"
                        f"容忍窗口: {task.grace_period}s\n"
                        f"当前时间: {fmt_bj(now)}"
                    ),
                    status="pending",
                )
                db.add(alert)
                await db.flush()

                # Send notifications
                await self._notify_for_task(db, task, alert)

            await db.commit()

    async def _notify_for_task(self, db: AsyncSession, task: ScheduledTask, alert: Alert):
        """Send notifications through all active channels for this task."""
        from app.services.notification import NotificationService

        rules_q = select(AlertRule).where(
            AlertRule.task_id == task.id,
            AlertRule.enabled == True,
            AlertRule.alert_type == "missed_run",
        )
        rules = (await db.execute(rules_q)).scalars().all()

        notifier = NotificationService()
        for rule in rules:
            channel = await db.get(NotificationChannel, rule.channel_id)
            if channel and channel.enabled:
                try:
                    await notifier.send(channel, alert.message)
                    logger.info("Alert sent for task %s via %s", task.name, channel.name)
                except Exception as exc:
                    logger.error("Failed to send alert for task %s via %s: %s",
                                 task.name, channel.name, exc)
