"""Database bootstrap helpers for a fresh local clone."""
import hashlib
import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.seeds import BASELINE_DRUGS
from app.models.drug import Drug
from app.models.user import User

logger = logging.getLogger(__name__)


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def seed_database(db: Session) -> dict[str, int]:
    """Seed default local data when the target tables are empty."""
    created = {"users": 0, "drugs": 0}

    if settings.SEED_DEFAULT_ADMIN:
        admin = db.query(User).filter_by(username=settings.DEFAULT_ADMIN_USERNAME).first()
        if not admin:
            db.add(
                User(
                    username=settings.DEFAULT_ADMIN_USERNAME,
                    password_hash=_hash_password(settings.DEFAULT_ADMIN_PASSWORD),
                    role="admin",
                    is_approved=True,
                )
            )
            created["users"] += 1

    if settings.SEED_BASELINE_DRUGS and db.query(Drug).count() == 0:
        for drug_data in BASELINE_DRUGS:
            db.add(Drug(**drug_data))
            created["drugs"] += 1

    if created["users"] or created["drugs"]:
        db.commit()
        logger.info("Seeded local database: %s", created)

    return created

