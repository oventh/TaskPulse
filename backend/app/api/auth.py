"""API router — Auth (login, me)."""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import LoginRequest, TokenResponse, UserInfo, UserOut
from app.services.auth import AuthService, create_access_token, decode_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    user = await svc.authenticate(body.username, body.password)
    if not user:
        raise HTTPException(401, detail="用户名或密码错误")
    token = create_access_token(user.id, user.username)
    return TokenResponse(
        access_token=token,
        user=UserInfo(id=user.id, username=user.username,
                      display_name=user.display_name, email=user.email),
    )


@router.get("/me", response_model=UserOut)
async def get_me(authorization: str = Header("", alias="Authorization"),
                 db: AsyncSession = Depends(get_db)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, detail="未登录")
    payload = decode_access_token(authorization[7:])
    if payload is None:
        raise HTTPException(401, detail="登录已过期，请重新登录")
    svc = AuthService(db)
    user = await svc.get_user_by_id(int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(401, detail="用户不存在或已停用")
    return UserOut(**user.__dict__)
