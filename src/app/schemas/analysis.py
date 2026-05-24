# Analysis Pydantic schemas for request validation and serialization
from pydantic import BaseModel
from typing import Optional, List
import datetime

class AnalysisCreate(BaseModel):
    name: str
    description: Optional[str] = None
    drug_ids: List[int]
    user_id: Optional[int] = None

class AnalysisItemResponse(BaseModel):
    id: int
    drug_name: str
    drug_id: int
    bp: Optional[float] = None
    vp: Optional[float] = None
    ev: Optional[float] = None
    fp: Optional[float] = None
    mr: Optional[float] = None
    st: Optional[float] = None
    mv: Optional[float] = None
    mw: Optional[float] = None
    complexity: Optional[float] = None

    class Config:
        from_attributes = True

class AnalysisResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime.datetime
    status: str
    folder_name: str
    items: List[AnalysisItemResponse] = []

    class Config:
        from_attributes = True
