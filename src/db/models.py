import datetime
from typing import Optional, List
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
import pathlib

# Using typical SQLAlchemy 2.0 types
class Base(DeclarativeBase):
    pass

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

class Analysis(Base):
    __tablename__ = 'analyses'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(1024))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft, processing, completed
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('users.id'))

    items: Mapped[List["AnalysisItem"]] = relationship("AnalysisItem", back_populates="analysis", cascade="all, delete-orphan")
    stats: Mapped[List["AnalysisStats"]] = relationship("AnalysisStats", back_populates="analysis", cascade="all, delete-orphan")
    user: Mapped[Optional["User"]] = relationship("User")

class AnalysisItem(Base):
    """
    Snapshot of a drug's properties for a specific analysis.
    Allows manual overrides without affecting the master Drug record.
    """
    __tablename__ = 'analysis_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey('analyses.id'))
    drug_id: Mapped[int] = mapped_column(ForeignKey('drugs.id'))
    
    # Snapshot of values (allows overrides)
    bp: Mapped[Optional[float]] = mapped_column(Float)
    vp: Mapped[Optional[float]] = mapped_column(Float)
    ev: Mapped[Optional[float]] = mapped_column(Float)
    fp: Mapped[Optional[float]] = mapped_column(Float)
    mr: Mapped[Optional[float]] = mapped_column(Float)
    st: Mapped[Optional[float]] = mapped_column(Float)
    mv: Mapped[Optional[float]] = mapped_column(Float)
    mw: Mapped[Optional[float]] = mapped_column(Float)
    complexity: Mapped[Optional[float]] = mapped_column(Float)

    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="items")
    drug: Mapped["Drug"] = relationship("Drug")

class AnalysisStats(Base):
    """Stores the calculated QSPR results for a specific analysis."""
    __tablename__ = 'analysis_stats'

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey('analyses.id'))
    
    property_name: Mapped[str] = mapped_column(String(50))
    index_name: Mapped[str] = mapped_column(String(50))
    
    r: Mapped[float] = mapped_column(Float)
    r2: Mapped[float] = mapped_column(Float)
    slope: Mapped[float] = mapped_column(Float)
    intercept: Mapped[float] = mapped_column(Float)
    p_value: Mapped[Optional[float]] = mapped_column(Float)
    rmse: Mapped[Optional[float]] = mapped_column(Float)
    f_statistic: Mapped[Optional[float]] = mapped_column(Float)
    adj_r2: Mapped[Optional[float]] = mapped_column(Float)
    n: Mapped[Optional[int]] = mapped_column(Integer)

    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="stats")

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="user") # admin, user
    is_approved: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"<User(username='{self.username}', role='{self.role}')>"

def get_engine(db_path: str = "data/drugs.db"):
    db_file = pathlib.Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{db_file.absolute()}", echo=False)

def init_db(engine):
    Base.metadata.create_all(engine)
    # Check if admin user exists, if not seed it
    from sqlalchemy.orm import Session
    import hashlib
    session = Session(engine)
    try:
        admin = session.query(User).filter_by(username="admin").first()
        if not admin:
            admin_user = User(
                username="admin",
                password_hash=hashlib.sha256("admin123".encode()).hexdigest(),
                role="admin",
                is_approved=True
            )
            session.add(admin_user)
            session.commit()
    except Exception as e:
        print(f"Error seeding admin: {e}")
    finally:
        session.close()

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
