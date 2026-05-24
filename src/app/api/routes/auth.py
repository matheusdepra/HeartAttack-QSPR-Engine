# Authentication API routes
from fastapi import APIRouter, Depends
from app.schemas.user import UserLogin, UserRegister, UserResponse
from app.services.auth_service import AuthService
from app.api.deps import get_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=UserResponse)
def login(data: UserLogin, auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.login(data)

@router.post("/register")
def register(data: UserRegister, auth_service: AuthService = Depends(get_auth_service)):
    user = auth_service.register(data)
    return {"status": "pending_approval", "message": "Solicitação enviada. Aguarde aprovação do administrador."}
