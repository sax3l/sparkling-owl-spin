import pytest, tempfile, os

# Placeholder for retention job
def retention_job(root, dry_run):
    # Simple logic: count files
    return len(os.listdir(root))

@pytest.mark.integration
def test_retention_job_noop_in_dev(tmp_path):
    path = tmp_path / "old_raw.html"
    path.write_text("...", encoding="utf-8")
    n = retention_job(root=str(tmp_path), dry_run=True)
    assert n >= 1