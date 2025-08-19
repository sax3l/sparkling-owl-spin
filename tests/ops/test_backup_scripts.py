import pytest, subprocess, sys

@pytest.mark.integration
def test_backup_script_exists_and_runs_dry():
    # This test assumes 'bash' is available and the script is executable.
    # It might fail on Windows or if permissions are incorrect.
    try:
        r = subprocess.run(["bash", "scripts/backup.sh", "--dry-run"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        assert r.returncode == 0
    except FileNotFoundError:
        pytest.skip("Bash or backup.sh not found.")