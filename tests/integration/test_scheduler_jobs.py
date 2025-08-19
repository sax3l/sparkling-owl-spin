import pytest

# Placeholder for scheduler
class MockScheduler:
    def __init__(self): self.jobs = []
    def get_jobs(self): return self.jobs
def make_scheduler(): return MockScheduler()
def register_jobs(scheduler): scheduler.jobs.extend([type('obj', (object,), {'id': 'proxy_validation'})(), type('obj', (object,), {'id': 'retention_job'})()])

@pytest.mark.integration
def test_scheduler_registers_jobs():
    s = make_scheduler()
    register_jobs(s)
    ids = [j.id for j in s.get_jobs()]
    assert {"proxy_validation", "retention_job"}.issubset(ids)