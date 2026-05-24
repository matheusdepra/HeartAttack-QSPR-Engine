# Drug library configuration endpoints
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.schemas.drug import DrugSchema
from app.services.drug_service import DrugService
from app.api.deps import get_drug_service

router = APIRouter(prefix="/drugs", tags=["drugs"])

@router.get("", response_model=List[DrugSchema])
def list_drugs(drug_service: DrugService = Depends(get_drug_service)):
    return drug_service.list_drugs()

@router.post("/sync")
def sync_drug(
    name: str, 
    smiles: Optional[str] = Query(None), 
    drug_service: DrugService = Depends(get_drug_service)
):
    return drug_service.sync_drug(name, smiles)

@router.put("/{id}")
def update_drug(id: int, data: dict, drug_service: DrugService = Depends(get_drug_service)):
    drug_service.update_drug(id, data)
    return {"status": "updated"}

@router.post("/{id}/resync")
def resync_drug(id: int, drug_service: DrugService = Depends(get_drug_service)):
    return drug_service.resync_drug(id)
