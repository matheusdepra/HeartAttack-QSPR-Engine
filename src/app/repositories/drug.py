# Data access layer for Drug entity
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.drug import Drug

class DrugRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[Drug]:
        return self.db.query(Drug).filter(Drug.id == id).first()

    def get_by_name(self, name: str) -> Optional[Drug]:
        return self.db.query(Drug).filter(Drug.name.ilike(name)).first()

    def list_all(self) -> List[Drug]:
        return self.db.query(Drug).order_by(Drug.name).all()

    def create(self, drug: Drug) -> Drug:
        self.db.add(drug)
        self.db.commit()
        self.db.refresh(drug)
        return drug

    def save(self, drug: Drug) -> Drug:
        self.db.commit()
        self.db.refresh(drug)
        return drug
