"""
Subscription Model
SQLAlchemy model for recurring subscriptions
"""
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from src.infrastructure.database.postgres import Base


class Subscription(Base):
    """Subscription model for tracking recurring payments."""
    
    __tablename__ = "subscriptions"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD")
    
    billing_cycle = Column(String(20), nullable=False)  # daily, weekly, monthly, yearly
    next_billing_date = Column(Date, nullable=False, index=True)
    
    category = Column(String(100), nullable=True)
    logo_url = Column(String(500), nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    canceled_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, name={self.name}, amount={self.amount})>"
