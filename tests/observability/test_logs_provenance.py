import pytest

# Placeholder for logger
def make_log_record(run_id, url):
    return f"run_id={run_id} url={url}"

@pytest.mark.unit
def test_log_has_provenance_fields():
    rec = make_log_record(run_id="run-1", url="http://x")
    assert "run_id=run-1" in rec and "url=http://x" in rec