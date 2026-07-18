# Facade: re-exports the refactored app for backwards-compatible uvicorn entrypoints.
# Run with: uvicorn api:app --reload --port 5555  (compatibility)
# Or:       uvicorn app.main:app --reload --port 5555  (new canonical entrypoint)
from app.main import app  # noqa: F401

if __name__ == "__main__":
    import uvicorn
    import os
    
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", "5555"))
    
    uvicorn.run(app, host=host, port=port, log_level="info")
