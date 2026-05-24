# User management endpoints (Admin features)
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.user import UserResponse, UserCreate
from app.repositories.user import UserRepository
from app.services.auth_service import AuthService
from app.api.deps import get_user_repo, get_auth_service

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=List[UserResponse])
def list_users(user_repo: UserRepository = Depends(get_user_repo)):
    return user_repo.list_all()

@router.post("", response_model=UserResponse)
def create_user(data: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.create_user(data)

@router.post("/{id}/approve", response_model=UserResponse)
def approve_user(id: int, user_repo: UserRepository = Depends(get_user_repo)):
    user = user_repo.get_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user.is_approved = True
    return user_repo.save(user)

@router.post("/{id}/toggle-role", response_model=UserResponse)
def toggle_user_role(id: int, user_repo: UserRepository = Depends(get_user_repo)):
    user = user_repo.get_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="Não é possível alterar o papel do administrador raiz.")
    user.role = "admin" if user.role == "user" else "user"
    return user_repo.save(user)

@router.delete("/{id}")
def delete_user(id: int, user_repo: UserRepository = Depends(get_user_repo)):
    user = user_repo.get_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="Não é possível excluir o administrador raiz.")
    user_repo.delete(user)
    return {"status": "deleted"}
