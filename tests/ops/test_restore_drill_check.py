import pytest, subprocess

@pytest.mark.integration
def test_restore_check_script():
    try:
        r = subprocess.run(["python", "scripts/restore_check.py", "--dry-run"], capture_output=True, text=True, check=False)
        assert r.returncode == 0
    except FileNotFoundError:
        pytest.skip("restore_check.py not found.")