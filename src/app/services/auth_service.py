# Business logic for user authentication and credentials management
import hashlib
from app.repositories.user import UserRepository
from app.models.user import User
from app.core.exceptions import AppError, InvalidCredentialsError
from app.schemas.user import UserLogin, UserRegister, UserCreate

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, schema: UserLogin) -> User:
        pw_hash = self.hash_password(schema.password)
        user = self.user_repo.get_by_username(schema.username)
        if not user or user.password_hash != pw_hash:
            raise InvalidCredentialsError("Credenciais inválidas")
        if not user.is_approved:
            raise AppError("Sua conta está pendente de aprovação por um administrador.", 403)
        return user

    def register(self, schema: UserRegister) -> User:
        existing = self.user_repo.get_by_username(schema.username)
        if existing:
            raise AppError("Este nome de usuário já está em uso.", 400)
            
        pw_hash = self.hash_password(schema.password)
        user = User(
            username=schema.username,
            password_hash=pw_hash,
            role="user",
            is_approved=False
        )
        return self.user_repo.create(user)

    def create_user(self, schema: UserCreate) -> User:
        existing = self.user_repo.get_by_username(schema.username)
        if existing:
            raise AppError("Este nome de usuário já está em uso.", 400)
            
        pw_hash = self.hash_password(schema.password)
        user = User(
            username=schema.username,
            password_hash=pw_hash,
            role=schema.role,
            is_approved=True
        )
        return self.user_repo.create(user)
