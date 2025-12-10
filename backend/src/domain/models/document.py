"""
Document Model
SQLAlchemy model for user documents
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from src.infrastructure.database.postgres import Base


class Document(Base):
    """Document model for storing user documents."""
    
    __tablename__ = "documents"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    filename = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)  # application/pdf, etc.
    file_size = Column(Integer, nullable=False)
    storage_path = Column(String(500), nullable=False)
    
    # Processing status
    status = Column(String(50), default="pending")  # pending, processing, ready, failed
    chunk_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, status={self.status})>"
