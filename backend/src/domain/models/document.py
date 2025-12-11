"""
Document Model
Stores metadata about uploaded documents
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from src.infrastructure.database.postgres import Base


class Document(Base):
    """Document metadata model."""
    
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes
    chunk_count = Column(Integer, default=0)
    
    description = Column(Text, nullable=True)
    status = Column(String(20), default="processing")  # processing, ready, failed
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="documents")
    
    def __repr__(self):
        return f"<Document {self.filename} ({self.status})>"
