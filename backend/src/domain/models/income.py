"""
Income Model
SQLAlchemy model for income tracking
"""
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from src.infrastructure.database.postgres import Base


class Income(Base):
    """Income model for tracking user income."""
    
    __tablename__ = "income"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD")
    source = Column(String(255), nullable=False)  # salary, freelance, investment, etc.
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    
    income_date = Column(Date, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="income")
    
    def __repr__(self):
        return f"<Income(id={self.id}, amount={self.amount}, source={self.source})>"
