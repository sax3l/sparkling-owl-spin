"""
GraphQL schema definition for ECaDP platform.

Defines the complete GraphQL schema including types, queries, mutations, and subscriptions.
"""

import graphene
from graphene import ObjectType, String, Int, Float, DateTime, Boolean, List, Field, ID
from graphene import Schema, Mutation, InputObjectType
from typing import Optional, Any
import logging

from .types import PersonType, CompanyType, VehicleType, DataQualityType
from .resolvers import QueryResolver, MutationResolver
from .mutations import (
    CreatePersonMutation, UpdatePersonMutation, DeletePersonMutation,
    CreateCompanyMutation, UpdateCompanyMutation, DeleteCompanyMutation,
    CreateVehicleMutation, UpdateVehicleMutation, DeleteVehicleMutation,
    StartScrapingJobMutation, CancelScrapingJobMutation
)

logger = logging.getLogger(__name__)


class Query(ObjectType):
    """Root Query type defining all available GraphQL queries."""
    
    # Person queries
    person = Field(PersonType, id=ID(required=True))
    persons = Field(List(PersonType), 
                   limit=Int(default_value=10),
                   offset=Int(default_value=0),
                   search=String(),
                   quality_level=String())
    
    # Company queries  
    company = Field(CompanyType, id=ID(required=True))
    companies = Field(List(CompanyType),
                     limit=Int(default_value=10), 
                     offset=Int(default_value=0),
                     search=String(),
                     industry=String())
    
    # Vehicle queries
    vehicle = Field(VehicleType, id=ID(required=True))
    vehicles = Field(List(VehicleType),
                    limit=Int(default_value=10),
                    offset=Int(default_value=0), 
                    search=String(),
                    make=String(),
                    model=String(),
                    year=Int())
    
    # Search across all entities
    search_all = Field(List(String), query=String(required=True))
    
    # Data quality queries
    data_quality_summary = Field(DataQualityType)
    
    # Resolver methods
    def resolve_person(self, info, id):
        return QueryResolver.resolve_person(info, id)
    
    def resolve_persons(self, info, limit=10, offset=0, search=None, quality_level=None):
        return QueryResolver.resolve_persons(info, limit, offset, search, quality_level)
    
    def resolve_company(self, info, id):
        return QueryResolver.resolve_company(info, id)
    
    def resolve_companies(self, info, limit=10, offset=0, search=None, industry=None):
        return QueryResolver.resolve_companies(info, limit, offset, search, industry)
    
    def resolve_vehicle(self, info, id):
        return QueryResolver.resolve_vehicle(info, id)
    
    def resolve_vehicles(self, info, limit=10, offset=0, search=None, make=None, model=None, year=None):
        return QueryResolver.resolve_vehicles(info, limit, offset, search, make, model, year)
    
    def resolve_search_all(self, info, query):
        return QueryResolver.resolve_search_all(info, query)
    
    def resolve_data_quality_summary(self, info):
        return QueryResolver.resolve_data_quality_summary(info)


class Mutation(ObjectType):
    """Root Mutation type defining all available GraphQL mutations."""
    
    # Person mutations
    create_person = CreatePersonMutation.Field()
    update_person = UpdatePersonMutation.Field()
    delete_person = DeletePersonMutation.Field()
    
    # Company mutations
    create_company = CreateCompanyMutation.Field()
    update_company = UpdateCompanyMutation.Field() 
    delete_company = DeleteCompanyMutation.Field()
    
    # Vehicle mutations
    create_vehicle = CreateVehicleMutation.Field()
    update_vehicle = UpdateVehicleMutation.Field()
    delete_vehicle = DeleteVehicleMutation.Field()
    
    # Scraping job mutations
    start_scraping_job = StartScrapingJobMutation.Field()
    cancel_scraping_job = CancelScrapingJobMutation.Field()


class Subscription(ObjectType):
    """Root Subscription type for real-time updates."""
    
    # Real-time data updates
    person_updated = Field(PersonType, person_id=ID())
    company_updated = Field(CompanyType, company_id=ID())
    vehicle_updated = Field(VehicleType, vehicle_id=ID())
    
    # Job status updates
    scraping_job_status = Field(String, job_id=ID(required=True))
    
    # Data quality alerts
    data_quality_alert = Field(String, threshold=Float(default_value=0.5))


# Create the main GraphQL schema
schema = Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
    auto_camelcase=False  # Keep field names as-is
)


def get_schema() -> Schema:
    """Get the GraphQL schema instance."""
    return schema


def create_schema_sdl() -> str:
    """Create Schema Definition Language (SDL) representation."""
    try:
        return str(schema)
    except Exception as e:
        logger.error(f"Error creating SDL: {e}")
        return ""


# Schema validation and introspection utilities
def validate_schema() -> bool:
    """Validate the GraphQL schema."""
    try:
        # Basic validation by attempting to get the schema
        schema.execute("{ __schema { types { name } } }")
        return True
    except Exception as e:
        logger.error(f"Schema validation failed: {e}")
        return False


def get_schema_types() -> List[str]:
    """Get list of all types in the schema."""
    try:
        result = schema.execute("{ __schema { types { name } } }")
        if result.data:
            return [t['name'] for t in result.data['__schema']['types']]
        return []
    except Exception as e:
        logger.error(f"Error getting schema types: {e}")
        return []


# Export the schema for use in FastAPI or other frameworks
__all__ = ["schema", "get_schema", "create_schema_sdl", "validate_schema", "get_schema_types"]
