# Predict topological indices from SMILES strings
from fastapi import APIRouter, Query, HTTPException
from app.schemas.predict import PredictResponse

router = APIRouter(prefix="/predict", tags=["predictor"])

@router.post("", response_model=PredictResponse)
def predict_smiles(smiles: str = Query(...)):
    try:
        from app.calculators.topological import calculate_for_drug
        ti = calculate_for_drug("Prediction", smiles)
        if ti is None:
            raise Exception("Invalid SMILES structure")
        return {"smiles": smiles, "indices": ti}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid SMILES: {str(e)}")
