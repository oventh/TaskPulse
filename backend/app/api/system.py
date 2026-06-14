"""API router — System configuration (base_url, etc.)."""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.system_config import SystemConfig

router = APIRouter(prefix="/api/system", tags=["system"])


class SystemConfigOut(BaseModel):
    base_url: str = ""
    scheduler_check_interval: int = 60


class SystemConfigUpdate(BaseModel):
    base_url: str = ""


@router.get("/config", response_model=SystemConfigOut)
async def get_system_config(request: Request, db: AsyncSession = Depends(get_db)):
    """返回系统配置。base_url 默认从请求 host 推断，也可从数据库读取用户配置。"""
    # Try to get from DB first
    stmt = select(SystemConfig).where(SystemConfig.key == "base_url")
    result = await db.execute(stmt)
    row = result.scalar_one_or_none()

    if row and row.value:
        base_url = row.value
    else:
        # Infer from request
        scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
        host = request.headers.get("host", request.url.hostname)
        base_url = f"{scheme}://{host}"

    return SystemConfigOut(
        base_url=base_url,
        scheduler_check_interval=60,
    )


@router.put("/config", response_model=SystemConfigOut)
async def update_system_config(body: SystemConfigUpdate, request: Request,
                                db: AsyncSession = Depends(get_db)):
    """更新系统配置并持久化到数据库。"""
    # Upsert base_url
    stmt = select(SystemConfig).where(SystemConfig.key == "base_url")
    result = await db.execute(stmt)
    row = result.scalar_one_or_none()

    if body.base_url:
        if row:
            row.value = body.base_url
        else:
            row = SystemConfig(key="base_url", value=body.base_url,
                               description="系统公网访问地址")
            db.add(row)
    else:
        # If clearing, remove from DB so we fall back to request host
        if row:
            await db.delete(row)

    await db.flush()
    await db.commit()

    # Return current effective config
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("host", request.url.hostname)
    effective_base = body.base_url or f"{scheme}://{host}"

    return SystemConfigOut(
        base_url=effective_base,
        scheduler_check_interval=60,
    )
