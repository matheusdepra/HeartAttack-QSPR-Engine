# Drug Pydantic schemas for request validation and serialization
from pydantic import BaseModel
from typing import Optional

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
    
    # Topological indices
    ti_abc: Optional[float] = None
    ti_ga: Optional[float] = None
    ti_ri: Optional[float] = None
    ti_rr: Optional[float] = None
    ti_h: Optional[float] = None
    ti_sci: Optional[float] = None
    ti_m1: Optional[float] = None
    ti_m2: Optional[float] = None
    ti_hm: Optional[float] = None
    ti_rm2: Optional[float] = None
    ti_f: Optional[float] = None
    ti_hf: Optional[float] = None
    
    class Config:
        from_attributes = True
