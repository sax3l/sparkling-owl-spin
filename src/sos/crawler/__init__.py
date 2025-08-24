"""
SOS Crawler Module

Innehåller crawling-funktionalitet inklusive template DSL och crawling engine.
"""

# Lazy import för att undvika cirkulära beroenden
def get_template_dsl():
    from .template_dsl import (
        TemplateModel,
        FollowRule, 
        FieldDef,
        Actions,
        RenderSpec,
        Limits,
        parse_template_yaml
    )
    return {
        'TemplateModel': TemplateModel,
        'FollowRule': FollowRule,
        'FieldDef': FieldDef,
        'Actions': Actions,
        'RenderSpec': RenderSpec,
        'Limits': Limits,
        'parse_template_yaml': parse_template_yaml
    }

__all__ = ['get_template_dsl']
