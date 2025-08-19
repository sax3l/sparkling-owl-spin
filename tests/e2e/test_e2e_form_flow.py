import pytest

@pytest.mark.e2e
@pytest.mark.browser
def test_form_flow(synthetic_hosts):
    pytest.skip("Selenium/Playwright not installed or configured for this test environment.")