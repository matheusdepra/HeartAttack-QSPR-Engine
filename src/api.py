from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
from pathlib import Path

from db.models import get_engine, get_session, init_db, Drug, Analysis, AnalysisItem, AnalysisStats, User
from scrapers.pubchem import process_drug_pubchem
from calculators.topological import calculate_for_drug
import hashlib
import re

app = FastAPI(title="CardioQSPR API")

# Enable CORS for React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Robust Asset Serving (Absolute Paths)
ROOT_DIR = Path(__file__).resolve().parent.parent
PLOTS_DIR = ROOT_DIR / "data" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/plots", StaticFiles(directory=str(PLOTS_DIR)), name="plots")

# Database Setup
engine = get_engine(db_path=str(ROOT_DIR / "data" / "drugs.db"))
init_db(engine)

def get_db():
    session = get_session(engine)
    try:
        yield session
    finally:
        session.close()

# --- Pydantic Models ---
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    is_approved: bool

    class Config:
        from_attributes = True

class DrugSchema(BaseModel):
    id: int
    name: str
    pubchem_cid: Optional[str] = None
    smiles: Optional[str] = None
    bp: Optional[float] = None
    vp: Optional[float] = None
    ev: Optional[float] = None
    fp: Optional[float] = None
    mr: Optional[float] = None
    st: Optional[float] = None
    mv: Optional[float] = None
    mw: Optional[float] = None
    complexity: Optional[float] = None
    bp_source: Optional[str] = None
    
    class Config:
        from_attributes = True

class AnalysisCreate(BaseModel):
    name: str
    description: Optional[str] = None
    drug_ids: List[int]
    user_id: Optional[int] = None

# --- Endpoints ---

@app.get("/api/drugs", response_model=List[DrugSchema])
def list_drugs(db=Depends(get_db)):
    return db.query(Drug).order_by(Drug.name).all()

@app.post("/api/drugs/sync")
def sync_drug(name: str, smiles: Optional[str] = None, db=Depends(get_db)):
    try:
        data = {}
        try:
            data = process_drug_pubchem(name)
        except Exception:
            pass
            
        final_smiles = smiles or data.get("smiles")
        if smiles:
            data["smiles"] = smiles
            
        if final_smiles:
            # Estimate missing properties from SMILES
            from scrapers.pubchem import (
                calculate_theoretical_bp,
                fetch_epi_suite_data
            )
            from rdkit import Chem
            from rdkit.Chem import Descriptors, Crippen
            from rdkit.Chem.GraphDescriptors import BertzCT
            
            try:
                mol = Chem.MolFromSmiles(final_smiles)
                if mol:
                    if data.get("mw") is None:
                        data["mw"] = round(Descriptors.MolWt(mol), 2)
                        data["mw_source"] = "Calculated (RDKit)"
                    if data.get("complexity") is None:
                        data["complexity"] = round(BertzCT(mol), 2)
                        data["complexity_source"] = "Calculated (RDKit BertzCT Proxy)"
                    if data.get("bp") is None:
                        calc_bp = calculate_theoretical_bp(final_smiles)
                        if calc_bp:
                            data["bp"] = calc_bp
                            data["bp_source"] = "Calculated (RDKit Estimator)"
                    if data.get("vp") is None:
                        epi = fetch_epi_suite_data(final_smiles)
                        if epi.get("vp"):
                            data["vp"] = epi["vp"]
                            data["vp_source"] = "Calculated (EPI Suite)"
                    if data.get("ev") is None and data.get("bp") is not None:
                        bp_k = data["bp"] + 273.15
                        data["ev"] = round(88 * bp_k / 1000, 2)
                        data["ev_source"] = "Calculated (RDKit/Trouton Estimate)"
                    if data.get("fp") is None and data.get("bp") is not None:
                        data["fp"] = round(0.683 * data["bp"] - 73, 2)
                        data["fp_source"] = "Calculated (Sinnott Rule)"
                    if data.get("mr") is None:
                        data["mr"] = round(Crippen.MolMR(mol), 2)
                        data["mr_source"] = "Calculated (RDKit Estimator)"
                    if data.get("st") is None and data.get("mr") is not None:
                        data["st"] = round(0.05 * data["mr"] * 10, 2)
                        data["st_source"] = "Calculated (Macleod-Sugden Proxy)"
                    if data.get("mv") is None:
                        data["mv"] = round(Descriptors.MolWt(mol) / 1.0, 2)
                        data["mv_source"] = "Calculated (MW/density=1 Approximation)"
            except Exception as e:
                logger.warning(f"RDKit estimations failed: {e}")
                    
        ti = calculate_for_drug(name, final_smiles) if final_smiles else None
        
        drug = Drug(
            name=name,
            **data,
            ti_abc=ti["ABC"] if ti else None,
            ti_ga=ti["GA"] if ti else None,
            ti_ri=ti["RI"] if ti else None,
            ti_rr=ti["RR"] if ti else None,
            ti_h=ti["H"] if ti else None,
            ti_sci=ti["SCI"] if ti else None,
            ti_m1=ti["M1"] if ti else None,
            ti_m2=ti["M2"] if ti else None,
            ti_hm=ti["HM"] if ti else None,
            ti_rm2=ti["RM2"] if ti else None,
            ti_f=ti["F"] if ti else None,
            ti_hf=ti["HF"] if ti else None,
        )
        db.add(drug)
        db.commit()
        db.refresh(drug)
        return drug
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/drugs/{id}")
def update_drug(id: int, data: dict, db=Depends(get_db)):
    drug = db.query(Drug).get(id)
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    
    old_smiles = drug.smiles
    new_smiles = data.get("smiles")
    
    for key, value in data.items():
        if hasattr(drug, key):
            setattr(drug, key, value)
            
    if new_smiles and new_smiles != old_smiles:
        ti = calculate_for_drug(drug.name, new_smiles)
        if ti:
            drug.ti_abc = ti.get("ABC")
            drug.ti_ga = ti.get("GA")
            drug.ti_ri = ti.get("RI")
            drug.ti_rr = ti.get("RR")
            drug.ti_h = ti.get("H")
            drug.ti_sci = ti.get("SCI")
            drug.ti_m1 = ti.get("M1")
            drug.ti_m2 = ti.get("M2")
            drug.ti_hm = ti.get("HM")
            drug.ti_rm2 = ti.get("RM2")
            drug.ti_f = ti.get("F")
            drug.ti_hf = ti.get("HF")
            
    db.commit()
    return {"status": "updated"}

@app.post("/api/drugs/{id}/resync")
def resync_drug(id: int, db=Depends(get_db)):
    drug = db.query(Drug).get(id)
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    
    try:
        # 1. Try finding data by Name
        data = process_drug_pubchem(drug.name)
        
        # 2. If name search failed but we have a SMILES, try finding properties by SMILES
        if (not data.get("pubchem_cid")) and drug.smiles:
            from scrapers.pubchem import get_cid_by_smiles, _get_json, PUBCHEM_VIEW, find_property_in_view
            cid = get_cid_by_smiles(drug.smiles)
            if cid:
                data["pubchem_cid"] = cid
                view_url = f"{PUBCHEM_VIEW}/data/compound/{cid}/JSON"
                view_data = _get_json(view_url, delay=0.5)
                bp, bp_src = find_property_in_view(view_data, ["Boiling Point"])
                vp, vp_src = find_property_in_view(view_data, ["Vapor Pressure"])
                # ... update data dict with found properties
                data.update({"bp": bp, "bp_source": bp_src, "vp": vp, "vp_source": vp_src})

        # Priority logic for SMILES: Existing > PubChem
        final_smiles = drug.smiles or data.get("smiles")
        
        # Update chemical properties (only if not already set or found new)
        for key, value in data.items():
            if value is not None:
                # If we already have a value and it's SMILES, we respect the priority
                if key == "smiles" and drug.smiles:
                    continue
                setattr(drug, key, value)
            
        if final_smiles:
            ti = calculate_for_drug(drug.name, final_smiles)
            if ti:
                drug.ti_abc = ti.get("ABC")
                drug.ti_ga = ti.get("GA")
                drug.ti_ri = ti.get("RI")
                drug.ti_rr = ti.get("RR")
                drug.ti_h = ti.get("H")
                drug.ti_sci = ti.get("SCI")
                drug.ti_m1 = ti.get("M1")
                drug.ti_m2 = ti.get("M2")
                drug.ti_hm = ti.get("HM")
                drug.ti_rm2 = ti.get("RM2")
                drug.ti_f = ti.get("F")
                drug.ti_hf = ti.get("HF")
        
        db.commit()
        db.refresh(drug)
        return drug
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Auth Endpoints ---

@app.post("/api/auth/login", response_model=UserResponse)
def auth_login(data: UserLogin, db=Depends(get_db)):
    pw_hash = hashlib.sha256(data.password.encode()).hexdigest()
    user = db.query(User).filter_by(username=data.username, password_hash=pw_hash).first()
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    if not user.is_approved:
        raise HTTPException(status_code=403, detail="Sua conta está pendente de aprovação por um administrador.")
    return user

@app.post("/api/auth/register")
def auth_register(data: UserRegister, db=Depends(get_db)):
    existing = db.query(User).filter_by(username=data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Este nome de usuário já está em uso.")
    
    pw_hash = hashlib.sha256(data.password.encode()).hexdigest()
    user = User(
        username=data.username,
        password_hash=pw_hash,
        role="user",
        is_approved=False
    )
    db.add(user)
    db.commit()
    return {"status": "pending_approval", "message": "Solicitação enviada. Aguarde aprovação do administrador."}

# --- User Management Endpoints ---

@app.get("/api/users", response_model=List[UserResponse])
def list_users(db=Depends(get_db)):
    return db.query(User).order_by(User.username).all()

@app.post("/api/users", response_model=UserResponse)
def create_user(data: UserCreate, db=Depends(get_db)):
    existing = db.query(User).filter_by(username=data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Este nome de usuário já está em uso.")
    
    pw_hash = hashlib.sha256(data.password.encode()).hexdigest()
    user = User(
        username=data.username,
        password_hash=pw_hash,
        role=data.role,
        is_approved=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/api/users/{id}/approve", response_model=UserResponse)
def approve_user(id: int, db=Depends(get_db)):
    user = db.query(User).get(id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user.is_approved = True
    db.commit()
    db.refresh(user)
    return user

@app.post("/api/users/{id}/toggle-role", response_model=UserResponse)
def toggle_user_role(id: int, db=Depends(get_db)):
    user = db.query(User).get(id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="Não é possível alterar o papel do administrador raiz.")
    user.role = "admin" if user.role == "user" else "user"
    db.commit()
    db.refresh(user)
    return user

@app.delete("/api/users/{id}")
def delete_user(id: int, db=Depends(get_db)):
    user = db.query(User).get(id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="Não é possível excluir o administrador raiz.")
    db.delete(user)
    db.commit()
    return {"status": "deleted"}

def get_analysis_folder_name(analysis) -> str:
    sanitized = re.sub(r'[^a-zA-Z0-9_\-]', '_', analysis.name)
    sanitized = sanitized.strip('_').lower()
    if not sanitized:
        sanitized = "analysis"
    return f"{sanitized}_{analysis.id}"

@app.get("/api/analyses")
def list_analyses(user_id: Optional[int] = None, db=Depends(get_db)):
    query = db.query(Analysis)
    if user_id is not None:
        query = query.filter_by(user_id=user_id)
    analyses = query.order_by(Analysis.created_at.desc()).all()
    res = []
    for a in analyses:
        res.append({
            "id": a.id,
            "name": a.name,
            "description": a.description,
            "created_at": a.created_at,
            "status": a.status,
            "user_id": a.user_id,
            "folder_name": get_analysis_folder_name(a)
        })
    return res

@app.post("/api/analyses")
def create_analysis(data: AnalysisCreate, db=Depends(get_db)):
    analysis = Analysis(name=data.name, description=data.description, user_id=data.user_id)
    db.add(analysis)
    db.commit()
    
    # Create snapshots for each drug
    for d_id in data.drug_ids:
        drug = db.query(Drug).get(d_id)
        if drug:
            item = AnalysisItem(
                analysis_id=analysis.id,
                drug_id=drug.id,
                bp=drug.bp,
                vp=drug.vp,
                ev=drug.ev,
                fp=drug.fp,
                mr=drug.mr,
                st=drug.st,
                mv=drug.mv,
                mw=drug.mw,
                complexity=drug.complexity
            )
            db.add(item)
    
    db.commit()
    return {
        "id": analysis.id,
        "name": analysis.name,
        "folder_name": get_analysis_folder_name(analysis)
    }

@app.get("/api/analyses/{id}")
def get_analysis(id: int, db=Depends(get_db)):
    analysis = db.query(Analysis).get(id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Return details including items
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
        "folder_name": get_analysis_folder_name(analysis),
        "items": items
    }

@app.put("/api/analyses/{id}/items/{item_id}")
def update_analysis_item(id: int, item_id: int, data: dict, db=Depends(get_db)):
    item = db.query(AnalysisItem).filter_by(id=item_id, analysis_id=id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for key, value in data.items():
        if hasattr(item, key):
            setattr(item, key, value)
    
    db.commit()
    return {"status": "updated"}

@app.post("/api/analyses/{id}/run")
def run_analysis(id: int, db=Depends(get_db)):
    from calculators.qspr import build_report
    from visualizers.report_plots import generate_structure_grid, generate_correlation_figures
    import pandas as pd
    import numpy as np

    analysis = db.query(Analysis).get(id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    folder_name = get_analysis_folder_name(analysis)
    try:
        # 1. Run QSPR
        output_dir = str(ROOT_DIR / f"data/qspr_results/{folder_name}")
        paths = build_report(db, output_dir=output_dir, analysis_id=id)
        
        # 2. Save Stats to DB
        all_models_df = pd.read_csv(paths['all_models'])
        # Clear old stats
        db.query(AnalysisStats).filter_by(analysis_id=id).delete()
        
        for _, row in all_models_df.iterrows():
            # Check if columns exist before getting them, or use defaults
            n_val = int(row.get('n', 0)) if pd.notnull(row.get('n')) else None
            adj_r2_val = float(row.get('adjusted_R2', np.nan)) if 'adjusted_R2' in row and pd.notnull(row['adjusted_R2']) else None
            
            # Re-calculate F-stat locally for saving if it wasn't saved in the CSV explicitly, but we have R2 and n
            # (or we could just calculate it on the fly)
            r2_val = float(row['R2'])
            f_stat = None
            if n_val and n_val > 2 and r2_val < 1.0:
                f_stat = (r2_val / (1.0 - r2_val)) * (n_val - 2)

            stat = AnalysisStats(
                analysis_id=id,
                property_name=row['property'],
                index_name=row['index'],
                r=row['r'],
                r2=r2_val,
                slope=row['slope'],
                intercept=row['intercept'],
                p_value=row['p_value'],
                rmse=row['RMSE'],
                adj_r2=adj_r2_val,
                n=n_val,
                f_statistic=f_stat
            )
            db.add(stat)
        
        # 3. Generate Plots
        plot_dir = str(ROOT_DIR / f"data/plots/{folder_name}")
        os.makedirs(plot_dir, exist_ok=True)
        
        drug_data = []
        for item in analysis.items:
            drug_data.append({'name': item.drug.name, 'smiles': item.drug.smiles})
        
        generate_structure_grid(pd.DataFrame(drug_data), os.path.join(plot_dir, "molecule_structures.png"))
        generate_correlation_figures(all_models_df, plot_dir)
        
        analysis.status = "completed"
        db.commit()
        
        return {"status": "completed", "report": str(paths['report'])}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analyses/{id}/report")
def get_analysis_report(id: int, db=Depends(get_db)):
    analysis = db.query(Analysis).get(id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    folder_name = get_analysis_folder_name(analysis)
    report_path = ROOT_DIR / f"data/qspr_results/{folder_name}/qspr_report.md"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not generated yet")
        
    return {"content": report_path.read_text(encoding="utf-8")}

@app.post("/api/predict")
def predict_smiles(smiles: str):
    try:
        ti = calculate_for_drug("Prediction", smiles)
        return {"smiles": smiles, "indices": ti}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid SMILES: {str(e)}")

@app.get("/api/health")
def health():
    return {"status": "ok"}
