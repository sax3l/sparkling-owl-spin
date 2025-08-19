import httpx
import uuid

class ECaDPClient:
    """Python SDK for the ECaDP API."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = ""):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.client = httpx.Client(base_url=self.base_url, headers=self.headers)

    def submit_crawl_job(self, start_url: str) -> dict:
        """Submits a new crawl job."""
        headers = {"Idempotency-Key": str(uuid.uuid4())}
        response = self.client.post("/jobs/crawl", json={"start_url": start_url}, headers=headers)
        response.raise_for_status()
        return response.json()

    # TODO: Implement other SDK methods