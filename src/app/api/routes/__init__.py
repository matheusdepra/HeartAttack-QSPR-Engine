# Expose routes in app.api.routes package
from app.api.routes import auth, users, drugs, analyses, predict, health

__all__ = ["auth", "users", "drugs", "analyses", "predict", "health"]
