import pytest
import subprocess

@pytest.mark.integration
def test_backup_script_exists_and_runs_dry():
    try:
        r = subprocess.run(["bash", "scripts/backup.sh", "--dry-run"], capture_output=True, text=True, check=False)
        assert r.returncode == 0
    except FileNotFoundError:
        pytest.skip("Bash or backup.sh not found.")