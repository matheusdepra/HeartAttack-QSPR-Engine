# Data access layer for Analysis, AnalysisItem, and AnalysisStats entities
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.analysis import Analysis, AnalysisItem, AnalysisStats

class AnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[Analysis]:
        return self.db.query(Analysis).filter(Analysis.id == id).first()

    def list_all(self, user_id: Optional[int] = None) -> List[Analysis]:
        query = self.db.query(Analysis)
        if user_id is not None:
            query = query.filter(Analysis.user_id == user_id)
        return query.order_by(Analysis.created_at.desc()).all()

    def create(self, analysis: Analysis) -> Analysis:
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def save(self, analysis: Analysis) -> Analysis:
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def get_item(self, id: int, analysis_id: int) -> Optional[AnalysisItem]:
        return self.db.query(AnalysisItem).filter_by(id=id, analysis_id=analysis_id).first()

    def create_item(self, item: AnalysisItem) -> AnalysisItem:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_stats(self, analysis_id: int) -> None:
        self.db.query(AnalysisStats).filter_by(analysis_id=analysis_id).delete()
        self.db.commit()

    def create_stat(self, stat: AnalysisStats) -> AnalysisStats:
        self.db.add(stat)
        self.db.commit()
        return stat

    def delete(self, analysis: Analysis) -> None:
        self.db.delete(analysis)
        self.db.commit()
