"""
GraphQL module for ECaDP platform.

Provides GraphQL API interface for querying and mutating scraped data.
"""

from .schema import schema
from .resolvers import QueryResolver, MutationResolver, SubscriptionResolver
from .types import PersonType, CompanyType, VehicleType
from .mutations import CreatePersonMutation, UpdatePersonMutation
from .subscriptions import DataUpdateSubscription

__all__ = [
    "schema",
    "QueryResolver", 
    "MutationResolver",
    "SubscriptionResolver",
    "PersonType",
    "CompanyType", 
    "VehicleType",
    "CreatePersonMutation",
    "UpdatePersonMutation",
    "DataUpdateSubscription"
]
