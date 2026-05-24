# Analysis, AnalysisItem, and AnalysisStats SQLAlchemy Database Models
import datetime
from typing import Optional, List
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

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
