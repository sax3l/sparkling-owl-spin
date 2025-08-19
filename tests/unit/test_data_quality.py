import pytest
from src.scraper.template_runtime import run_template

@pytest.mark.unit
def test_dq_score_calculation():
    """
    Verifies that the weighted DQ score is calculated correctly based on its components.
    """
    # This test uses the stubbed implementation of run_template.
    # As the real implementation is built, this test will ensure the formula remains correct.
    
    _record, dq_metrics = run_template("<html></html>", {"id": "test-template"})
    
    assert "completeness" in dq_metrics
    assert "validity" in dq_metrics
    assert "consistency" in dq_metrics
    assert "dq_score" in dq_metrics
    
    # Expected score based on stub: (0.4 * 0.98) + (0.4 * 1.0) + (0.2 * 0.95) = 0.392 + 0.4 + 0.19 = 0.982
    expected_score = 0.982
    
    assert dq_metrics["dq_score"] == pytest.approx(expected_score)