"""
Goal Model
SQLAlchemy model for financial goals
"""
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from src.infrastructure.database.postgres import Base


class Goal(Base):
    """Goal model for tracking financial goals."""
    
    __tablename__ = "goals"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    target_amount = Column(Numeric(12, 2), nullable=False)
    current_amount = Column(Numeric(12, 2), default=0)
    currency = Column(String(3), default="USD")
    
    category = Column(String(100), nullable=True)
    deadline = Column(Date, nullable=False)
    
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="goals")
    
    @property
    def progress_percent(self) -> float:
        """Calculate progress percentage."""
        if self.target_amount == 0:
            return 0.0
        return float(self.current_amount / self.target_amount * 100)
    
    def __repr__(self):
        return f"<Goal(id={self.id}, name={self.name}, progress={self.progress_percent:.1f}%)>"
