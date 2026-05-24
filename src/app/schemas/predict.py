# Predict Pydantic schemas for request validation and serialization
from pydantic import BaseModel
from typing import Dict, Optional

class PredictResponse(BaseModel):
    smiles: str
    indices: Optional[Dict[str, float]] = None
