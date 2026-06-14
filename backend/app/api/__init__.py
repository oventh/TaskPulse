"""API __init__ + shared dependencies."""

from fastapi import Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Agent
from app.services import AgentService


async def verify_api_key(
    authorization: str = Header("", alias="Authorization"),
    db: AsyncSession = None,  # injected via Depends in router
) -> Agent:
    """Dependency: verify API Key in Authorization header."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    api_key = authorization[7:]
    svc = AgentService(db)
    agent = await svc.get_by_api_key(api_key)
    if agent is None:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    if agent.status != "active":
        raise HTTPException(status_code=403, detail="Agent is inactive")
    return agent
