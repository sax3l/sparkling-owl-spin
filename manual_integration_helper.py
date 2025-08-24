#!/usr/bin/env python3
"""
Manual Integration Helper
========================

Baserat på GitHub repository-analysen, detta verktyg hjälper till med 
manuell integration av rekommenderade funktioner.

Fokuserar på de högst prioriterade repositories:
- requests-ip-rotator (HIGH priority)
- selenium-proxy-rotator (HIGH priority) 

Skapar säkra, manuellt granskade integrations-templates.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


class ManualIntegrationHelper:
    """
    Hjälper till med manuell integration av analyserade repositories.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
        # Data från analysen
        self.high_priority_repos = [
            {
                "name": "requests-ip-rotator",
                "url": "https://github.com/Ge0rg3/requests-ip-rotator",
                "features": ["proxy_management"],
                "complexity": 11.36,
                "integration_notes": "Enkel, välstrukturerad proxy rotator för requests"
            },
            {
                "name": "selenium-proxy-rotator", 
                "url": "https://github.com/markgacoka/selenium-proxy-rotator",
                "features": ["proxy_management"],
                "complexity": 30.32,
                "integration_notes": "Proxy rotator specifikt för Selenium WebDriver"
            }
        ]
        
    def create_integration_templates(self):
        """Skapa manuella integrations-templates."""
        
        print("🛠️  SKAPAR MANUAL INTEGRATION TEMPLATES")
        print("=" * 60)
        
        for repo in self.high_priority_repos:
            print(f"\n📦 Repository: {repo['name']}")
            print(f"🔗 URL: {repo['url']}")
            print(f"⚙️  Komplexitet: {repo['complexity']}")
            print(f"📝 Kommentar: {repo['integration_notes']}")
            
            self._create_integration_template(repo)
            
        print(f"\n✅ Alla templates skapade i: {self.project_root / 'integration_templates'}")
        
    def _create_integration_template(self, repo: dict):
        """Skapa integration template för specifikt repository."""
        
        template_dir = self.project_root / "integration_templates" / repo['name']
        template_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Integration plan
        self._create_integration_plan(template_dir, repo)
        
        # 2. Code template
        self._create_code_template(template_dir, repo)
        
        # 3. Test template
        self._create_test_template(template_dir, repo)
        
        print(f"   ✅ Template skapad: {template_dir}")
        
    def _create_integration_plan(self, template_dir: Path, repo: dict):
        """Skapa integrations-plan."""
        
        plan_content = f"""
# Integration Plan: {repo['name']}

## Repository Information
- **URL**: {repo['url']}
- **Features**: {', '.join(repo['features'])}
- **Complexity Score**: {repo['complexity']}
- **Priority**: HIGH

## Integration Strategy

### 1. Manual Review Steps
1. Clone repository manually: `git clone {repo['url']}`
2. Review source code for key functionality
3. Identify core classes and functions
4. Test functionality independently
5. Adapt for our architecture

### 2. Integration Approach

#### For requests-ip-rotator:
- Target module: `src/proxy_pool/ip_rotator.py`
- Key features to extract:
  - IP rotation logic
  - AWS API Gateway integration  
  - Request session management
- Integration points:
  - Enhance existing ProxyPoolManager
  - Add IP rotation capabilities

#### For selenium-proxy-rotator:
- Target module: `src/proxy_pool/selenium_rotator.py`
- Key features to extract:
  - WebDriver proxy switching
  - Proxy validation for Selenium
  - Browser session management
- Integration points:
  - New module for Selenium-specific proxy handling
  - Integration with existing scraper components

### 3. Manual Testing Required
- [ ] Verify proxy rotation works
- [ ] Test with different proxy sources
- [ ] Validate error handling
- [ ] Performance testing
- [ ] Integration with existing components

### 4. Rollback Plan
- Keep original modules intact
- Create new modules with '_integrated' suffix
- Use feature flags for gradual deployment

## Notes
{repo['integration_notes']}

## Next Steps
1. Manual code review
2. Create adapted version  
3. Unit testing
4. Integration testing
5. Documentation update

---
Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        with open(template_dir / "INTEGRATION_PLAN.md", 'w', encoding='utf-8') as f:
            f.write(plan_content)
            
    def _create_code_template(self, template_dir: Path, repo: dict):
        """Skapa kod-template."""
        
        if repo['name'] == 'requests-ip-rotator':
            code_template = '''"""
Enhanced IP Rotator Integration
Based on: https://github.com/Ge0rg3/requests-ip-rotator

Manual integration template - REVIEW AND ADAPT BEFORE USE
"""

import requests
from typing import List, Optional, Dict, Any
import random
import time
from utils.logger import get_logger
from observability.metrics import MetricsCollector

logger = get_logger(__name__)


class EnhancedIPRotator:
    """
    Manual integration of IP rotator functionality.
    
    Based on analysis of requests-ip-rotator repository.
    This is a TEMPLATE - adapt according to actual repository code.
    """
    
    def __init__(self, proxy_list: List[str], metrics: MetricsCollector):
        self.proxy_list = proxy_list
        self.metrics = metrics
        self.current_proxy_index = 0
        self.session = requests.Session()
        
        logger.info(f"IP Rotator initialized with {len(proxy_list)} proxies")
        
    def get_next_proxy(self) -> Optional[str]:
        """Get next proxy in rotation."""
        try:
            if not self.proxy_list:
                return None
                
            proxy = self.proxy_list[self.current_proxy_index]
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
            
            logger.debug(f"Using proxy: {proxy}")
            self.metrics.counter('proxy_rotator.proxy_used', 1)
            
            return proxy
            
        except Exception as e:
            logger.error(f"Error getting next proxy: {e}")
            return None
            
    def make_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make request with proxy rotation."""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                proxy = self.get_next_proxy()
                if not proxy:
                    break
                    
                proxies = {'http': proxy, 'https': proxy}
                
                response = self.session.get(url, proxies=proxies, **kwargs)
                
                if response.status_code == 200:
                    self.metrics.counter('proxy_rotator.successful_requests', 1)
                    return response
                    
            except Exception as e:
                logger.warning(f"Proxy request failed (attempt {attempt + 1}): {e}")
                self.metrics.counter('proxy_rotator.failed_requests', 1)
                
        logger.error(f"All proxy attempts failed for {url}")
        return None


# TODO: Manual integration steps:
# 1. Review actual repository code
# 2. Extract key functionality
# 3. Adapt to our architecture 
# 4. Add proper error handling
# 5. Create comprehensive tests
'''

        elif repo['name'] == 'selenium-proxy-rotator':
            code_template = '''"""
Selenium Proxy Rotator Integration
Based on: https://github.com/markgacoka/selenium-proxy-rotator

Manual integration template - REVIEW AND ADAPT BEFORE USE
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from typing import List, Optional, Dict, Any
import random
from utils.logger import get_logger
from observability.metrics import MetricsCollector

logger = get_logger(__name__)


class SeleniumProxyRotator:
    """
    Manual integration of Selenium proxy rotator.
    
    Based on analysis of selenium-proxy-rotator repository.
    This is a TEMPLATE - adapt according to actual repository code.
    """
    
    def __init__(self, proxy_list: List[str], metrics: MetricsCollector):
        self.proxy_list = proxy_list
        self.metrics = metrics
        self.current_proxy_index = 0
        self.driver = None
        
        logger.info(f"Selenium Proxy Rotator initialized with {len(proxy_list)} proxies")
        
    def get_driver_with_proxy(self) -> Optional[webdriver.Chrome]:
        """Create WebDriver instance with rotated proxy."""
        try:
            proxy = self._get_next_proxy()
            if not proxy:
                return None
                
            chrome_options = Options()
            chrome_options.add_argument(f'--proxy-server={proxy}')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=chrome_options)
            
            logger.info(f"WebDriver created with proxy: {proxy}")
            self.metrics.counter('selenium_proxy_rotator.drivers_created', 1)
            
            return driver
            
        except Exception as e:
            logger.error(f"Failed to create WebDriver with proxy: {e}")
            self.metrics.counter('selenium_proxy_rotator.driver_creation_failed', 1)
            return None
            
    def _get_next_proxy(self) -> Optional[str]:
        """Get next proxy in rotation."""
        if not self.proxy_list:
            return None
            
        proxy = self.proxy_list[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
        
        return proxy
        
    def rotate_proxy(self, driver: webdriver.Chrome) -> Optional[webdriver.Chrome]:
        """Rotate to new proxy by recreating driver."""
        try:
            if driver:
                driver.quit()
                
            return self.get_driver_with_proxy()
            
        except Exception as e:
            logger.error(f"Failed to rotate proxy: {e}")
            return None


# TODO: Manual integration steps:
# 1. Review actual repository code
# 2. Extract key functionality  
# 3. Adapt to our WebDriver setup
# 4. Add proper error handling
# 5. Create comprehensive tests
# 6. Test with different proxy sources
'''
        
        with open(template_dir / f"{repo['name']}_template.py", 'w', encoding='utf-8') as f:
            f.write(code_template)
            
    def _create_test_template(self, template_dir: Path, repo: dict):
        """Skapa test-template."""
        
        test_template = f'''"""
Test template for {repo['name']} integration.

Manual testing guidelines - ADAPT BEFORE USE
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class Test{repo['name'].replace('-', '').title()}Integration:
    """Test class for {repo['name']} integration."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        # TODO: Implement after manual code review
        assert True, "Placeholder test"
        
    def test_proxy_rotation(self):
        """Test proxy rotation logic.""" 
        # TODO: Implement proxy rotation tests
        assert True, "Placeholder test"
        
    def test_error_handling(self):
        """Test error handling."""
        # TODO: Implement error handling tests
        assert True, "Placeholder test"
        
    def test_integration_with_existing_code(self):
        """Test integration with existing components."""
        # TODO: Test integration points
        assert True, "Placeholder test"


# Manual testing checklist:
# [ ] Test with real proxies
# [ ] Test error scenarios
# [ ] Test performance under load
# [ ] Test integration with existing proxy pool
# [ ] Test cleanup and resource management

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
        
        with open(template_dir / f"test_{repo['name']}_integration.py", 'w', encoding='utf-8') as f:
            f.write(test_template)
            
    def generate_integration_summary(self):
        """Generera sammanfattning av integration templates."""
        
        summary_content = f"""
# GitHub Repository Integration Summary

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Analysis Results
- **Total repositories analyzed**: 5
- **High priority recommendations**: 2
- **Medium priority recommendations**: 3
- **Low priority recommendations**: 0

## High Priority Integrations Created

### 1. requests-ip-rotator
- **Complexity**: Low (11.36)
- **Features**: IP rotation, AWS integration  
- **Template Location**: `integration_templates/requests-ip-rotator/`
- **Next Steps**: Manual code review and adaptation

### 2. selenium-proxy-rotator  
- **Complexity**: Medium (30.32)
- **Features**: Selenium WebDriver proxy rotation
- **Template Location**: `integration_templates/selenium-proxy-rotator/`
- **Next Steps**: Manual code review and adaptation

## Manual Integration Workflow

1. **Review Templates**: Check generated integration plans
2. **Clone Repositories**: Manually clone the recommended repos
3. **Code Review**: Analyze actual source code 
4. **Adapt Templates**: Modify templates based on actual code
5. **Testing**: Implement comprehensive tests
6. **Integration**: Gradually integrate with existing code
7. **Validation**: Verify functionality and performance

## Integration Benefits

### Expected Improvements:
- Enhanced proxy rotation capabilities
- Better IP management for scraping
- Selenium-specific proxy handling
- Reduced detection risk
- Improved scraping reliability

### Risk Mitigation:
- Manual review process prevents automatic integration errors
- Templates provide structured approach
- Rollback plans included
- Feature flags for gradual deployment

## Next Steps

1. Review integration plans in `integration_templates/`
2. Manually clone and analyze recommended repositories
3. Adapt templates based on actual code structure  
4. Implement comprehensive tests
5. Gradually integrate features

---

**Note**: All integration templates are manually reviewable and require 
human validation before implementation. No automatic code integration 
has been performed.
"""
        
        summary_file = self.project_root / "GITHUB_INTEGRATION_SUMMARY.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
            
        print(f"📄 Integration summary: {summary_file}")


def main():
    """Huvudfunktion för manual integration helper."""
    
    project_root = Path(__file__).parent
    
    helper = ManualIntegrationHelper(project_root)
    
    print("🛠️  GITHUB REPOSITORY MANUAL INTEGRATION HELPER")
    print("=" * 60)
    
    # Skapa templates
    helper.create_integration_templates()
    
    # Skapa sammanfattning
    helper.generate_integration_summary()
    
    print("\n🎉 MANUAL INTEGRATION TEMPLATES SKAPADE!")
    print("📋 Nästa steg:")
    print("   1. Granska integration_templates/ katalogen")
    print("   2. Läs GITHUB_INTEGRATION_SUMMARY.md")
    print("   3. Klona repositories manuellt för kodgranskning")
    print("   4. Anpassa templates baserat på verklig kod")
    print("   5. Implementera tester")
    print("   6. Gradvis integration")


if __name__ == "__main__":
    main()
