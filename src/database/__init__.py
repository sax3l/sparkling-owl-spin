"""
Database Module - Data storage and management.

Provides comprehensive database functionality including:
- Connection management and pooling
- Model definitions and relationships
- Migration support
- Query optimization
- Data validation and constraints
- Audit trails and lineage tracking

Main Components:
- DatabaseManager: Core database operations
- ConnectionManager: Connection pooling and health
- ModelDefinitions: Data models and schemas
- MigrationManager: Schema evolution
"""

from .manager import DatabaseManager
from .connection import ConnectionManager
from .models import (
    PersonModel, CompanyModel, VehicleModel,
    ScrapingJobModel, TemplateModel, DataQualityModel
)

# Convenience alias
DatabaseManager = DatabaseManager

__all__ = [
    "DatabaseManager", 
    "ConnectionManager",
    "PersonModel",
    "CompanyModel", 
    "VehicleModel",
    "ScrapingJobModel",
    "TemplateModel",
    "DataQualityModel"
]