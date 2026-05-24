# Drug SQLAlchemy Database Model
import datetime
from typing import Optional
from sqlalchemy import String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Drug(Base):
    __tablename__ = 'drugs'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(1024))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    
    # PubChem data
    pubchem_cid: Mapped[Optional[str]] = mapped_column(String(50))
    smiles: Mapped[Optional[str]] = mapped_column(String(1024))
    
    # Properties and their sources (experimental or computed)
    bp: Mapped[Optional[float]] = mapped_column(Float)
    bp_source: Mapped[Optional[str]] = mapped_column(String(50))
    
    vp: Mapped[Optional[float]] = mapped_column(Float)
    vp_source: Mapped[Optional[str]] = mapped_column(String(50))
    
    ev: Mapped[Optional[float]] = mapped_column(Float)
    ev_source: Mapped[Optional[str]] = mapped_column(String(50))
    
    fp: Mapped[Optional[float]] = mapped_column(Float)
    fp_source: Mapped[Optional[str]] = mapped_column(String(50))
    
    mr: Mapped[Optional[float]] = mapped_column(Float)
    mr_source: Mapped[Optional[str]] = mapped_column(String(50))
    
    st: Mapped[Optional[float]] = mapped_column(Float)
    st_source: Mapped[Optional[str]] = mapped_column(String(50))
    
    mv: Mapped[Optional[float]] = mapped_column(Float)
    mv_source: Mapped[Optional[str]] = mapped_column(String(50))
    
    mw: Mapped[Optional[float]] = mapped_column(Float)
    mw_source: Mapped[Optional[str]] = mapped_column(String(50))
    
    complexity: Mapped[Optional[float]] = mapped_column(Float)
    complexity_source: Mapped[Optional[str]] = mapped_column(String(50))

    # Topological indices (degree-based)
    ti_abc: Mapped[Optional[float]] = mapped_column(Float)
    ti_ga:  Mapped[Optional[float]] = mapped_column(Float)
    ti_ri:  Mapped[Optional[float]] = mapped_column(Float)
    ti_rr:  Mapped[Optional[float]] = mapped_column(Float)
    ti_h:   Mapped[Optional[float]] = mapped_column(Float)
    ti_sci: Mapped[Optional[float]] = mapped_column(Float)
    ti_m1:  Mapped[Optional[float]] = mapped_column(Float)
    ti_m2:  Mapped[Optional[float]] = mapped_column(Float)
    ti_hm:  Mapped[Optional[float]] = mapped_column(Float)
    ti_rm2: Mapped[Optional[float]] = mapped_column(Float)
    ti_f:   Mapped[Optional[float]] = mapped_column(Float)
    ti_hf:  Mapped[Optional[float]] = mapped_column(Float)

    def __repr__(self) -> str:
        return f"<Drug(name='{self.name}', cid='{self.pubchem_cid}')>"
