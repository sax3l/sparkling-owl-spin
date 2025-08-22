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

from .manager import DatabaseManager, get_db, get_database_manager
from .connection import DatabaseConnection, DatabaseMigrator
try:
    from .models import (
        PersonModel, CompanyModel, VehicleModel,
        ScrapingJobModel, TemplateModel, DataQualityModel
    )
except ImportError:
    # Models might not be available yet
    PersonModel = CompanyModel = VehicleModel = None
    ScrapingJobModel = TemplateModel = DataQualityModel = None

__all__ = [
    "DatabaseManager", 
    "DatabaseConnection",
    "DatabaseMigrator",
    "get_db",
    "get_database_manager",
    "PersonModel",
    "CompanyModel", 
    "VehicleModel",
    "ScrapingJobModel",
    "TemplateModel",
    "DataQualityModel"
]