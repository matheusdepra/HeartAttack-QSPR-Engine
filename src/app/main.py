# Main FastAPI application entrypoint
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core.exceptions import register_exception_handlers
from app.api.router import router as api_router
from app.db.bootstrap import seed_database

# Ensure all tables are created on startup
Base.metadata.create_all(bind=engine)
if settings.AUTO_SEED_DATABASE:
    with SessionLocal() as db:
        seed_database(db)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
)

# CORS — allow all origins for dev/OCI deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for generated plots
app.mount(settings.STATIC_PLOTS_ROUTE, StaticFiles(directory=str(settings.PLOTS_DIR)), name="plots")

# Register centralised exception handlers
register_exception_handlers(app)

# Mount all API routes under configured prefix
app.include_router(api_router, prefix=settings.API_PREFIX)
