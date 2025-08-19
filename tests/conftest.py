# Pytest fixtures will be defined here.
import pytest

@pytest.fixture(scope="session")
def http_client():
    # A fixture for the HTTP client, for example.
    pass