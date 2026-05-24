# Master router aggregating all subroutes
from fastapi import APIRouter
from app.api.routes import auth, users, drugs, analyses, predict, health

router = APIRouter()

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(drugs.router)
router.include_router(analyses.router)
router.include_router(predict.router)
router.include_router(health.router)
