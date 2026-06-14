"""API router — Notifications & Alerts."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    AlertAcknowledge,
    AlertOut,
    AlertRuleCreate,
    AlertRuleOut,
    NotificationChannelCreate,
    NotificationChannelOut,
    NotificationChannelUpdate,
)
from app.models import Alert, AlertRule, NotificationChannel, ScheduledTask

router = APIRouter(prefix="/api", tags=["notifications"])


# ── Notification Channels ─────────────────────────────────────────────

@router.post("/notification-channels", response_model=NotificationChannelOut, status_code=201)
async def create_channel(body: NotificationChannelCreate, db: AsyncSession = Depends(get_db)):
    channel = NotificationChannel(
        name=body.name,
        channel_type=body.channel_type,
        config=body.config,
    )
    db.add(channel)
    await db.flush()
    await db.refresh(channel)
    await db.commit()
    return NotificationChannelOut(**channel.__dict__)


@router.get("/notification-channels", response_model=list[NotificationChannelOut])
async def list_channels(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(select(NotificationChannel).order_by(NotificationChannel.id))
    channels = result.scalars().all()
    return [NotificationChannelOut(**c.__dict__) for c in channels]


@router.put("/notification-channels/{channel_id}", response_model=NotificationChannelOut)
async def update_channel(channel_id: int, body: NotificationChannelUpdate,
                         db: AsyncSession = Depends(get_db)):
    channel = await db.get(NotificationChannel, channel_id)
    if not channel:
        raise HTTPException(404, "Channel not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(channel, k, v)
    await db.flush()
    await db.commit()
    return NotificationChannelOut(**channel.__dict__)


@router.delete("/notification-channels/{channel_id}", status_code=204)
async def delete_channel(channel_id: int, db: AsyncSession = Depends(get_db)):
    channel = await db.get(NotificationChannel, channel_id)
    if not channel:
        raise HTTPException(404, "Channel not found")
    await db.delete(channel)
    await db.flush()
    await db.commit()


# ── Alert Rules ───────────────────────────────────────────────────────

@router.post("/alert-rules", response_model=AlertRuleOut, status_code=201)
async def create_alert_rule(body: AlertRuleCreate, db: AsyncSession = Depends(get_db)):
    # Verify task & channel exist
    task = await db.get(ScheduledTask, body.task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    channel = await db.get(NotificationChannel, body.channel_id)
    if not channel:
        raise HTTPException(404, "Channel not found")

    rule = AlertRule(
        task_id=body.task_id,
        channel_id=body.channel_id,
        alert_type=body.alert_type,
    )
    db.add(rule)
    await db.flush()
    await db.refresh(rule)
    await db.commit()
    return AlertRuleOut(**{**rule.__dict__, "channel_name": channel.name})


@router.get("/alert-rules", response_model=list[AlertRuleOut])
async def list_alert_rules(task_id: int | None = Query(None), db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    stmt = select(AlertRule)
    if task_id:
        stmt = stmt.where(AlertRule.task_id == task_id)
    result = await db.execute(stmt)
    rules = result.scalars().all()
    output = []
    for r in rules:
        ch = await db.get(NotificationChannel, r.channel_id)
        output.append(AlertRuleOut(**{**r.__dict__, "channel_name": ch.name if ch else ""}))
    return output


@router.delete("/alert-rules/{rule_id}", status_code=204)
async def delete_alert_rule(rule_id: int, db: AsyncSession = Depends(get_db)):
    rule = await db.get(AlertRule, rule_id)
    if not rule:
        raise HTTPException(404, "Alert rule not found")
    await db.delete(rule)
    await db.flush()
    await db.commit()


# ── Alerts ────────────────────────────────────────────────────────────

@router.get("/alerts", response_model=list[AlertOut])
async def list_alerts(
    status: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select, desc
    stmt = select(Alert).order_by(desc(Alert.id)).offset(offset).limit(limit)
    if status:
        stmt = stmt.where(Alert.status == status)
    result = await db.execute(stmt)
    alerts = result.scalars().all()
    output = []
    for a in alerts:
        task_name = ""
        if a.task_id:
            task = await db.get(ScheduledTask, a.task_id)
            task_name = task.name if task else ""
        output.append(AlertOut(**{**a.__dict__, "task_name": task_name}))
    return output


@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertOut)
async def acknowledge_alert(alert_id: int, body: AlertAcknowledge,
                            db: AsyncSession = Depends(get_db)):
    from datetime import datetime
    alert = await db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.status = "acknowledged"
    alert.acknowledged_at = datetime.utcnow()
    await db.flush()
    await db.commit()

    task_name = ""
    if alert.task_id:
        task = await db.get(ScheduledTask, alert.task_id)
        task_name = task.name if task else ""
    return AlertOut(**{**alert.__dict__, "task_name": task_name})
