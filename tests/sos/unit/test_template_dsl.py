"""
Unit tests för SOS Template DSL parser

Testar YAML parsing, validering och transformation av crawling templates.
"""

import pytest
import yaml
from pydantic import ValidationError

from sos.crawler.template_dsl import (
    TemplateModel, 
    FollowRule, 
    FieldDef, 
    Actions, 
    RenderSpec, 
    Limits,
    parse_template_yaml
)


class TestTemplateDSL:
    """Test suite för Template DSL parsing och validering"""
    
    def test_minimal_template_parsing(self):
        """Test parsing av minimal template"""
        yaml_content = """
        name: "Minimal Test"
        start_urls:
          - "https://example.com"
        """
        
        template = parse_template_yaml(yaml_content)
        
        assert template.name == "Minimal Test"
        assert template.start_urls == ["https://example.com"]
        assert len(template.follow) == 0
        assert len(template.extract) == 0
        assert template.render.enabled is False
        assert template.limits.max_pages == 500  # default
        assert template.delay_ms == 1000  # default
        
    def test_complex_template_parsing(self, sample_template_yaml):
        """Test parsing av komplex template med alla fält"""
        template = parse_template_yaml(sample_template_yaml)
        
        # Grundläggande fält
        assert template.name == "Test Template"
        assert len(template.start_urls) == 1
        
        # Follow rules
        assert len(template.follow) == 2
        pagination_rule = next(r for r in template.follow if r.type == "pagination")
        assert pagination_rule.selector == "a.next-page"
        
        detail_rule = next(r for r in template.follow if r.type == "detail") 
        assert detail_rule.selector == ".item-link"
        
        # Extract fields
        assert len(template.extract) == 2
        title_field = next(f for f in template.extract if f.name == "title")
        assert title_field.selector == "h1"
        assert title_field.type == "text"
        
        price_field = next(f for f in template.extract if f.name == "price")
        assert price_field.regex == "([0-9,]+)"
        
        # Settings
        assert template.render.enabled is False
        assert template.actions.scroll is False
        assert template.limits.max_pages == 10
        assert template.delay_ms == 1500
        
    def test_invalid_yaml_raises_error(self):
        """Test att invalid YAML ger fel"""
        invalid_yaml = """
        name: "Invalid"
        start_urls:
          - invalid_url_without_protocol
        follow:
          - invalid_selector_structure
        """
        
        with pytest.raises((ValidationError, yaml.YAMLError)):
            parse_template_yaml(invalid_yaml)
            
    def test_missing_required_fields(self):
        """Test att saknade required fields ger ValidationError"""
        incomplete_yaml = """
        # name saknas
        start_urls:
          - "https://example.com"
        """
        
        with pytest.raises(ValidationError):
            parse_template_yaml(incomplete_yaml)
            
    def test_field_def_validation(self):
        """Test validering av FieldDef"""
        
        # Valid field
        field = FieldDef(
            name="test",
            selector="h1", 
            type="text"
        )
        assert field.name == "test"
        assert field.attr is None
        
        # Field med attribute
        attr_field = FieldDef(
            name="link",
            selector="a",
            type="attr",
            attr="href"
        )
        assert attr_field.attr == "href"
        
    def test_follow_rule_validation(self):
        """Test validering av FollowRule"""
        
        # Basic follow rule
        rule = FollowRule(selector="a.link")
        assert rule.type == "generic"  # default
        assert rule.match is None
        
        # Follow rule med match filter
        filtered_rule = FollowRule(
            selector="a",
            match="*/product/*",
            type="detail"
        )
        assert filtered_rule.match == "*/product/*"
        assert filtered_rule.type == "detail"
        
    def test_actions_defaults(self):
        """Test Actions default values"""
        actions = Actions()
        
        assert actions.scroll is False
        assert actions.scroll_max == 0
        assert actions.wait_ms == 0
        assert actions.click_selector is None
        
    def test_limits_validation(self):
        """Test Limits validation"""
        limits = Limits()
        
        assert limits.max_pages == 500
        assert limits.max_depth == 5
        
        # Custom limits
        custom_limits = Limits(max_pages=100, max_depth=3)
        assert custom_limits.max_pages == 100
        assert custom_limits.max_depth == 3
        
    def test_render_spec(self):
        """Test RenderSpec configuration"""
        
        # Default - no rendering
        render = RenderSpec()
        assert render.enabled is False
        
        # Enabled rendering
        render_enabled = RenderSpec(enabled=True)
        assert render_enabled.enabled is True


class TestTemplateValidation:
    """Avancerade validering-tester för templates"""
    
    def test_url_validation(self):
        """Test att URL:er valideras korrekt"""
        
        # Giltiga URLs
        valid_template = """
        name: "Valid URLs"
        start_urls:
          - "https://example.com"
          - "http://test.org/path"
        """
        
        template = parse_template_yaml(valid_template)
        assert len(template.start_urls) == 2
        
    def test_selector_field_combinations(self):
        """Test olika kombinationer av selectors och field types"""
        
        template_yaml = """
        name: "Selector Test" 
        start_urls:
          - "https://example.com"
        extract:
          - name: "text_field"
            selector: ".content"
            type: "text"
          - name: "html_field" 
            selector: ".raw"
            type: "html"
          - name: "attr_field"
            selector: "img"
            type: "attr"
            attr: "src"
          - name: "regex_field"
            selector: ".price"
            type: "text"
            regex: "\\\\$([0-9,\\\\.]+)"
        """
        
        template = parse_template_yaml(template_yaml)
        
        # Kontrollera att alla fält tolkats korrekt
        fields = {f.name: f for f in template.extract}
        
        assert fields["text_field"].type == "text"
        assert fields["html_field"].type == "html" 
        assert fields["attr_field"].attr == "src"
        assert fields["regex_field"].regex == "\\$([0-9,\\.]+)"
        
    def test_complex_actions_configuration(self):
        """Test komplex actions-konfiguration"""
        
        actions_yaml = """
        name: "Complex Actions"
        start_urls:
          - "https://example.com"
        actions:
          scroll: true
          scroll_max: 5
          wait_ms: 3000
          click_selector: "button.load-more"
        """
        
        template = parse_template_yaml(actions_yaml)
        
        assert template.actions.scroll is True
        assert template.actions.scroll_max == 5
        assert template.actions.wait_ms == 3000
        assert template.actions.click_selector == "button.load-more"
