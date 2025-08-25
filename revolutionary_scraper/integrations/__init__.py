#!/usr/bin/env python3
"""
GitHub Integrations Package - Revolutionary Ultimate System v4.0
Centralized package for all GitHub repository integrations
"""

from .github_registry import (
    registry,
    IntegrationCategory,
    IntegrationInfo,
    load_integration,
    execute_integration_operation,
    get_integration_info,
    list_available_integrations,
    get_integration_recommendations,
    perform_integration_health_check,
    get_integration_statistics
)

__all__ = [
    'registry',
    'IntegrationCategory',
    'IntegrationInfo',
    'load_integration',
    'execute_integration_operation',
    'get_integration_info',
    'list_available_integrations',
    'get_integration_recommendations',
    'perform_integration_health_check',
    'get_integration_statistics'
]
