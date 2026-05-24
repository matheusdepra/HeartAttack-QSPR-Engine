# QSPR regression execution and reporting endpoints
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from app.schemas.analysis import AnalysisCreate
from app.services.analysis_service import AnalysisService
from app.api.deps import get_analysis_service

router = APIRouter(prefix="/analyses", tags=["analyses"])

@router.get("")
def list_analyses(
    user_id: Optional[int] = Query(None), 
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    analyses = analysis_service.list_analyses(user_id)
    res = []
    for a in analyses:
        res.append({
            "id": a.id,
            "name": a.name,
            "description": a.description,
            "created_at": a.created_at,
            "status": a.status,
            "user_id": a.user_id,
            "folder_name": analysis_service.get_analysis_folder_name(a)
        })
    return res

@router.post("")
def create_analysis(
    data: AnalysisCreate, 
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    analysis = analysis_service.create_analysis(
        name=data.name, 
        drug_ids=data.drug_ids, 
        description=data.description, 
        user_id=data.user_id
    )
    return {
        "id": analysis.id,
        "name": analysis.name,
        "folder_name": analysis_service.get_analysis_folder_name(analysis)
    }

@router.get("/{id}")
def get_analysis(id: int, analysis_service: AnalysisService = Depends(get_analysis_service)):
    analysis = analysis_service.get_analysis(id)
    items = []
    for item in analysis.items:
        items.append({
            "id": item.id,
            "drug_name": item.drug.name,
            "drug_id": item.drug_id,
            "bp": item.bp,
            "vp": item.vp,
            "ev": item.ev,
            "fp": item.fp,
            "mr": item.mr,
            "st": item.st,
            "mv": item.mv,
            "mw": item.mw,
            "complexity": item.complexity
        })
    
    return {
        "id": analysis.id,
        "name": analysis.name,
        "description": analysis.description,
        "created_at": analysis.created_at,
        "status": analysis.status,
        "folder_name": analysis_service.get_analysis_folder_name(analysis),
        "items": items
    }

@router.put("/{id}/items/{item_id}")
def update_analysis_item(
    id: int, 
    item_id: int, 
    data: dict, 
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    analysis_service.update_analysis_item(id, item_id, data)
    return {"status": "updated"}

@router.post("/{id}/run")
def run_analysis(id: int, analysis_service: AnalysisService = Depends(get_analysis_service)):
    return analysis_service.run_analysis(id)

@router.get("/{id}/report")
def get_analysis_report(id: int, analysis_service: AnalysisService = Depends(get_analysis_service)):
    content = analysis_service.get_analysis_report(id)
    return {"content": content}

@router.delete("/{id}")
def delete_analysis(id: int, analysis_service: AnalysisService = Depends(get_analysis_service)):
    analysis_service.delete_analysis(id)
    return {"status": "deleted"}

@router.get("/{id}/stats")
def get_analysis_stats(id: int, analysis_service: AnalysisService = Depends(get_analysis_service)):
    analysis = analysis_service.get_analysis(id)
    res = []
    for stat in analysis.stats:
        res.append({
            "id": stat.id,
            "property_name": stat.property_name,
            "index_name": stat.index_name,
            "r": stat.r,
            "r2": stat.r2,
            "slope": stat.slope,
            "intercept": stat.intercept,
            "p_value": stat.p_value,
            "rmse": stat.rmse,
            "adj_r2": stat.adj_r2,
            "n": stat.n,
            "f_statistic": stat.f_statistic
        })
    return res
