from typing import Optional
from sqlalchemy import String, Float, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
import pathlib

# Using typical SQLAlchemy 2.0 types
class Base(DeclarativeBase):
    pass

class Drug(Base):
    __tablename__ = 'drugs'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(1024))
    
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

    # Topological indices (degree-based)
    ti_ri:  Mapped[Optional[float]] = mapped_column(Float)   # Randic Index
    ti_rr:  Mapped[Optional[float]] = mapped_column(Float)   # Reciprocal Randic
    ti_h:   Mapped[Optional[float]] = mapped_column(Float)   # Harmonic Index
    ti_sci: Mapped[Optional[float]] = mapped_column(Float)   # Sum Connectivity
    ti_m1:  Mapped[Optional[float]] = mapped_column(Float)   # First Zagreb
    ti_m2:  Mapped[Optional[float]] = mapped_column(Float)   # Second Zagreb
    ti_hm:  Mapped[Optional[float]] = mapped_column(Float)   # Hyper Zagreb
    ti_rm2: Mapped[Optional[float]] = mapped_column(Float)   # Redefined Second Zagreb
    ti_f:   Mapped[Optional[float]] = mapped_column(Float)   # Forgotten Index
    ti_hf:  Mapped[Optional[float]] = mapped_column(Float)   # Hyper Forgotten Index

    def __repr__(self) -> str:
        return f"<Drug(name='{self.name}', cid='{self.pubchem_cid}')>"

def get_engine(db_path: str = "data/drugs.db"):
    db_file = pathlib.Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{db_file.absolute()}", echo=False)

def init_db(engine):
    Base.metadata.create_all(engine)

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
