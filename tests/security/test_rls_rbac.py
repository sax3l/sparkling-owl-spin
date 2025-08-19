import os, pytest

@pytest.mark.db
def test_rls_blocks_unauthorized_select():
    pytest.skip("Database connection not configured for this test.")