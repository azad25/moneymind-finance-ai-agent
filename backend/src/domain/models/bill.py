"""
Bill Model
SQLAlchemy model for bill tracking
"""
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from src.infrastructure.database.postgres import Base


class Bill(Base):
    """Bill model for tracking due payments."""
    
    __tablename__ = "bills"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD")
    
    due_date = Column(Date, nullable=False, index=True)
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50), nullable=True)  # monthly, weekly, etc.
    
    is_paid = Column(Boolean, default=False)
    paid_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="bills")
    
    def __repr__(self):
        return f"<Bill(id={self.id}, name={self.name}, due_date={self.due_date})>"
