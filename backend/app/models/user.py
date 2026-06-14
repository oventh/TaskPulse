"""SQLAlchemy models — User (dashboard login)."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    """Dashboard user for login authentication."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, comment="登录用户名")
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False, comment="bcrypt 密码哈希")
    display_name: Mapped[str] = mapped_column(String(128), default="", comment="显示名称")
    email: Mapped[str] = mapped_column(String(128), default="", comment="邮箱")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<User {self.username}>"
