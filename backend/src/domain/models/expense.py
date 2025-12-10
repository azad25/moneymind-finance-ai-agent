"""
Expense Model
SQLAlchemy model for expense tracking
"""
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from src.infrastructure.database.postgres import Base


class Expense(Base):
    """Expense model for tracking user expenses."""
    
    __tablename__ = "expenses"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD")
    category = Column(String(100), nullable=False, index=True)
    merchant = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    expense_date = Column(Date, nullable=False, index=True)
    
    # Source tracking
    source = Column(String(50), default="manual")  # manual, email, import
    source_id = Column(String(255), nullable=True)  # email_id, transaction_id, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="expenses")
    
    def __repr__(self):
        return f"<Expense(id={self.id}, amount={self.amount}, merchant={self.merchant})>"
