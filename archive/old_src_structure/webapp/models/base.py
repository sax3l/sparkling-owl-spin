"""
Base database model with common fields and functionality.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class BaseModel(Base):
    """Base model with common fields for all database models."""
    
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(255), nullable=True)  # User ID who created this record
    updated_by = Column(String(255), nullable=True)  # User ID who last updated this record
    
    # Metadata for tracking changes and context
    metadata_json = Column(Text, nullable=True)  # JSON field for additional metadata
    tags = Column(Text, nullable=True)  # Comma-separated tags
    
    def to_dict(self, exclude_fields: Optional[list] = None) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        exclude_fields = exclude_fields or []
        result = {}
        
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                elif hasattr(value, '__str__'):
                    value = str(value)
                result[column.name] = value
                
        return result
    
    def update_from_dict(self, data: Dict[str, Any], allowed_fields: Optional[list] = None) -> None:
        """Update model fields from dictionary."""
        allowed_fields = allowed_fields or [col.name for col in self.__table__.columns]
        
        for key, value in data.items():
            if key in allowed_fields and hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def get_table_name(cls) -> str:
        """Get the table name for this model."""
        return cls.__tablename__
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"
