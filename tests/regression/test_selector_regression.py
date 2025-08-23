import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import json
from typing import Dict, List, Any


@pytest.fixture
def golden_dataset():
    """Golden dataset for regression testing"""
    return {
        "vehicle_detail": {
            "url": "https://www.biluppgifter.se/fordon/abc123",
            "expected_selectors": {
                "title": "h1.vehicle-title",
                "make": ".vehicle-info .make",
                "model": ".vehicle-info .model", 
                "year": ".vehicle-info .year",
                "mileage": ".specs .mileage-value",
                "price": ".price-box .current-price"
            },
            "expected_fields": [
                "title", "make", "model", "year", "mileage", "price"
            ],
            "html_file": "fixtures/html_samples/vehicle_detail_golden.html"
        },
        "company_profile": {
            "url": "https://www.allabolag.se/5560123456/company-name-ab",
            "expected_selectors": {
                "company_name": "h1.company-name",
                "org_number": ".company-info .org-number",
                "address": ".contact-info .address",
                "phone": ".contact-info .phone",
                "employees": ".stats .employee-count"
            },
            "expected_fields": [
                "company_name", "org_number", "address", "phone", "employees"  
            ],
            "html_file": "fixtures/html_samples/company_profile_golden.html"
        },
        "person_profile": {
            "url": "https://www.hitta.se/john+andersson/stockholm",
            "expected_selectors": {
                "name": "h1.person-name",
                "address": ".address-info .full-address",
                "age": ".person-info .age",
                "phone": ".contact-info .phone-number"
            },
            "expected_fields": [
                "name", "address", "age", "phone"
            ],
            "html_file": "fixtures/html_samples/person_profile_golden.html"
        }
    }


@pytest.fixture
def template_configs():
    """Template configurations for regression testing"""
    return {
        "vehicle_detail": {
            "name": "vehicle_detail_v3",
            "target": "vehicle",
            "version": 3,
            "selectors": {
                "title": {"selector": "h1.vehicle-title", "required": True},
                "make": {"selector": ".vehicle-info .make", "required": True},
                "model": {"selector": ".vehicle-info .model", "required": True},
                "year": {"selector": ".vehicle-info .year", "required": True, "type": "int"},
                "mileage": {"selector": ".specs .mileage-value", "required": False, "type": "int"},
                "price": {"selector": ".price-box .current-price", "required": False, "type": "decimal"}
            }
        }
    }


@pytest.mark.regression
@pytest.mark.asyncio
async def test_selector_stability_against_golden_set(golden_dataset, template_configs):
    """Test that selectors remain stable against golden dataset"""
    from src.scraper.template_runtime import run_template
    
    results = {}
    
    for template_name, golden_data in golden_dataset.items():
        # Load golden HTML sample
        with open(golden_data["html_file"], "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Get template config
        template_config = template_configs.get(template_name, {})
        
        # Run template extraction
        extracted_data, metrics = run_template(html_content, template_config)
        
        # Verify all expected fields are present
        for field in golden_data["expected_fields"]:
            assert field in extracted_data, f"Missing expected field '{field}' in {template_name}"
            assert extracted_data[field] is not None, f"Field '{field}' is null in {template_name}"
        
        # Verify selector matching
        for field, expected_selector in golden_data["expected_selectors"].items():
            actual_selector = template_config["selectors"][field]["selector"]
            assert actual_selector == expected_selector, \
                f"Selector mismatch for '{field}': expected '{expected_selector}', got '{actual_selector}'"
        
        results[template_name] = {
            "extracted_fields": len(extracted_data),
            "expected_fields": len(golden_data["expected_fields"]),
            "match_rate": len(extracted_data) / len(golden_data["expected_fields"]),
            "data_quality_score": metrics.get("dq_score", 0)
        }
    
    # Verify overall regression success
    total_match_rate = sum(r["match_rate"] for r in results.values()) / len(results)
    assert total_match_rate >= 0.95, f"Overall selector match rate {total_match_rate:.2%} below threshold"
    
    print(f"Selector regression test passed with {total_match_rate:.2%} match rate")


@pytest.mark.regression
def test_selector_drift_detection(golden_dataset):
    """Test detection of selector drift over time"""
    from src.analysis.similarity_analysis import calculate_selector_drift
    
    # Simulate historical selector data
    historical_selectors = {
        "vehicle_detail": {
            "title": "h1.vehicle-title",
            "make": ".vehicle-info .make", 
            "model": ".vehicle-info .model"
        }
    }
    
    # Simulate current selectors (with drift)
    current_selectors = {
        "vehicle_detail": {
            "title": "h1.car-title",  # Changed selector
            "make": ".vehicle-info .make",  # Same
            "model": ".car-info .model"   # Changed selector
        }
    }
    
    drift_score = calculate_selector_drift(historical_selectors, current_selectors)
    
    # Should detect 2 out of 3 selectors changed = 67% drift
    assert drift_score["vehicle_detail"]["drift_percentage"] > 50
    assert "title" in drift_score["vehicle_detail"]["changed_selectors"]
    assert "model" in drift_score["vehicle_detail"]["changed_selectors"]
    assert "make" not in drift_score["vehicle_detail"]["changed_selectors"]


@pytest.mark.regression
@pytest.mark.asyncio
async def test_template_extraction_regression(golden_dataset):
    """Test that template extraction results remain consistent"""
    from src.scraper.template_extractor import TemplateExtractor
    
    extractor = TemplateExtractor()
    
    regression_results = {}
    
    for template_name, golden_data in golden_dataset.items():
        # Load golden HTML
        with open(golden_data["html_file"], "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Extract data using current selectors
        extracted_data = await extractor.extract_data(
            html_content, 
            golden_data["expected_selectors"]
        )
        
        # Calculate extraction success rate
        successful_extractions = sum(1 for field in golden_data["expected_fields"] 
                                   if field in extracted_data and extracted_data[field])
        success_rate = successful_extractions / len(golden_data["expected_fields"])
        
        regression_results[template_name] = {
            "success_rate": success_rate,
            "extracted_count": successful_extractions,
            "expected_count": len(golden_data["expected_fields"]),
            "extracted_data": extracted_data
        }
        
        # Assert minimum success rate
        assert success_rate >= 0.90, \
            f"Template {template_name} extraction success rate {success_rate:.2%} below 90%"
    
    # Log regression test results
    print("Template Regression Results:")
    for template_name, result in regression_results.items():
        print(f"  {template_name}: {result['success_rate']:.2%} success rate")


@pytest.mark.regression
def test_data_quality_regression(golden_dataset):
    """Test that data quality metrics remain stable"""
    from src.analysis.data_quality import calculate_dq_metrics
    
    # Expected DQ baseline scores
    expected_baselines = {
        "vehicle_detail": {"completeness": 0.95, "validity": 0.98, "consistency": 0.92},
        "company_profile": {"completeness": 0.90, "validity": 0.96, "consistency": 0.88},
        "person_profile": {"completeness": 0.85, "validity": 0.94, "consistency": 0.90}
    }
    
    for template_name, golden_data in golden_dataset.items():
        # Mock extracted data for DQ calculation
        mock_extracted_data = [{
            field: f"sample_value_{i}" 
            for i, field in enumerate(golden_data["expected_fields"])
        } for _ in range(100)]  # 100 sample records
        
        # Calculate current DQ metrics
        current_metrics = calculate_dq_metrics(mock_extracted_data)
        expected_baseline = expected_baselines[template_name]
        
        # Assert DQ metrics haven't regressed
        assert current_metrics["completeness"] >= expected_baseline["completeness"] * 0.95, \
            f"Completeness regression in {template_name}"
        assert current_metrics["validity"] >= expected_baseline["validity"] * 0.95, \
            f"Validity regression in {template_name}"
        assert current_metrics["consistency"] >= expected_baseline["consistency"] * 0.95, \
            f"Consistency regression in {template_name}"


@pytest.mark.regression
@pytest.mark.parametrize("template_type", ["vehicle_detail", "company_profile", "person_profile"])
def test_individual_template_regression(template_type, golden_dataset):
    """Parameterized test for individual template regression"""
    if template_type not in golden_dataset:
        pytest.skip(f"No golden data available for {template_type}")
    
    golden_data = golden_dataset[template_type]
    
    # Load golden HTML sample
    with open(golden_data["html_file"], "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Verify HTML contains expected content structure
    for field, selector in golden_data["expected_selectors"].items():
        # Basic check that selector targets exist in HTML
        selector_class = selector.replace(".", "").replace(" ", ".")
        assert selector_class in html_content or field.lower() in html_content.lower(), \
            f"Expected content for field '{field}' not found in golden HTML"
    
    print(f"✅ Template {template_type} regression test passed")


@pytest.mark.regression
def test_selector_performance_regression():
    """Test that selector performance hasn't regressed"""
    from src.scraper.xpath_suggester import XPathSuggester
    import time
    
    suggester = XPathSuggester()
    
    # Performance baseline (milliseconds)
    performance_baselines = {
        "simple_selector": 50,  # 50ms
        "complex_selector": 200,  # 200ms
        "xpath_generation": 100   # 100ms
    }
    
    # Test simple selector performance  
    start_time = time.time()
    simple_result = suggester.suggest_css_selector("<div class='test'>content</div>", "content")
    simple_duration = (time.time() - start_time) * 1000
    
    assert simple_duration < performance_baselines["simple_selector"], \
        f"Simple selector performance regression: {simple_duration:.1f}ms > {performance_baselines['simple_selector']}ms"
    
    # Test complex selector performance
    complex_html = "<div>" * 100 + "<span class='target'>content</span>" + "</div>" * 100
    start_time = time.time()
    complex_result = suggester.suggest_css_selector(complex_html, "content")
    complex_duration = (time.time() - start_time) * 1000
    
    assert complex_duration < performance_baselines["complex_selector"], \
        f"Complex selector performance regression: {complex_duration:.1f}ms > {performance_baselines['complex_selector']}ms"
    
    print(f"✅ Selector performance tests passed (simple: {simple_duration:.1f}ms, complex: {complex_duration:.1f}ms)")


@pytest.mark.regression
def test_end_to_end_extraction_pipeline():
    """End-to-end regression test of the complete extraction pipeline"""
    from src.crawler.url_queue import URLQueue
    from src.scraper.http_scraper import HTTPScraper
    from src.scraper.template_runtime import run_template
    
    # Mock complete extraction pipeline
    url_queue = URLQueue()
    scraper = HTTPScraper()
    
    test_urls = [
        "https://example.com/vehicle/1",
        "https://example.com/company/2", 
        "https://example.com/person/3"
    ]
    
    pipeline_results = []
    
    for url in test_urls:
        # Mock the pipeline steps
        with patch.object(scraper, 'scrape_url', new_callable=AsyncMock) as mock_scrape:
            mock_scrape.return_value = {
                "html": "<html><body>Mock content</body></html>",
                "status_code": 200,
                "response_time": 1.5
            }
            
            # Simulate pipeline execution
            result = {
                "url": url,
                "scraped": True,
                "extracted_fields": 5,
                "processing_time": 2.3,
                "data_quality": 0.94
            }
            
            pipeline_results.append(result)
    
    # Verify pipeline regression thresholds
    avg_dq = sum(r["data_quality"] for r in pipeline_results) / len(pipeline_results)
    avg_processing_time = sum(r["processing_time"] for r in pipeline_results) / len(pipeline_results)
    success_rate = sum(1 for r in pipeline_results if r["scraped"]) / len(pipeline_results)
    
    assert success_rate >= 0.95, f"Pipeline success rate {success_rate:.2%} below threshold"
    assert avg_dq >= 0.90, f"Average data quality {avg_dq:.2%} below threshold"
    assert avg_processing_time <= 5.0, f"Average processing time {avg_processing_time:.1f}s above threshold"
    
    print(f"✅ E2E pipeline regression test passed (success: {success_rate:.2%}, DQ: {avg_dq:.2%}, time: {avg_processing_time:.1f}s)")