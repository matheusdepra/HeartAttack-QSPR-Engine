# FastAPI dependencies injecting DB sessions, repositories, and services
import secrets
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.repositories.user import UserRepository
from app.repositories.drug import DrugRepository
from app.repositories.analysis import AnalysisRepository
from app.services.auth_service import AuthService
from app.services.drug_service import DrugService
from app.services.analysis_service import AnalysisService

# Repositories
def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_drug_repo(db: Session = Depends(get_db)) -> DrugRepository:
    return DrugRepository(db)

def get_analysis_repo(db: Session = Depends(get_db)) -> AnalysisRepository:
    return AnalysisRepository(db)

# Services
def get_auth_service(user_repo: UserRepository = Depends(get_user_repo)) -> AuthService:
    return AuthService(user_repo)

def get_drug_service(drug_repo: DrugRepository = Depends(get_drug_repo)) -> DrugService:
    return DrugService(drug_repo)

def get_analysis_service(
    analysis_repo: AnalysisRepository = Depends(get_analysis_repo),
    drug_repo: DrugRepository = Depends(get_drug_repo)
) -> AnalysisService:
    return AnalysisService(analysis_repo, drug_repo)


def require_admin_api_key(x_admin_api_key: Optional[str] = Header(default=None)) -> None:
    """Protect admin-only endpoints when ADMIN_API_KEY is configured."""
    if not settings.ADMIN_API_KEY:
        return
    if not x_admin_api_key or not secrets.compare_digest(x_admin_api_key, settings.ADMIN_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin API key",
        )
