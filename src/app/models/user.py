# User SQLAlchemy Database Model
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="user")  # admin, user
    is_approved: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"<User(username='{self.username}', role='{self.role}')>"
