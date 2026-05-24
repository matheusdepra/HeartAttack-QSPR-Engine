# Facade: re-exports the refactored app for backwards-compatible uvicorn entrypoints.
# Run with: uvicorn api:app --reload --port 5555  (legacy)
# Or:       uvicorn app.main:app --reload --port 5555  (new canonical entrypoint)
from app.main import app  # noqa: F401
