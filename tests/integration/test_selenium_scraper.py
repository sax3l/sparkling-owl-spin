import pytest

@pytest.mark.integration
@pytest.mark.browser
def test_browser_smoke():
    pytest.skip("Selenium/Playwright not installed or configured for this test environment.")