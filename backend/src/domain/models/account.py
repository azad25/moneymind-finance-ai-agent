"""
Account Model
SQLAlchemy model for user account/balance tracking
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.infrastructure.database.postgres import Base


class Account(Base):
    """Account model for tracking user account balances."""
    
    __tablename__ = "accounts"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    name = Column(String(255), default="Main Account", nullable=False)
    account_type = Column(String(50), default="checking")  # checking, savings, credit_card, cash
    currency = Column(String(3), default="USD")
    
    current_balance = Column(Numeric(12, 2), default=0, nullable=False)
    
    # Timestamps
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    
    def __repr__(self):
        return f"<Account(id={self.id}, name={self.name}, balance={self.current_balance})>"
