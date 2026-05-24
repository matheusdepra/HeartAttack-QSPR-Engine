# Data access layer for User entity
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter_by(username=username).first()

    def list_all(self) -> List[User]:
        return self.db.query(User).order_by(User.username).all()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()

    def save(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user
