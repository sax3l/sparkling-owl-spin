import httpx
from playwright.sync_api import sync_playwright
from src.anti_bot.policy_manager import DomainPolicy

class TransportManager:
    """
    Abstracts the fetching mechanism, allowing for dynamic switching
    between simple HTTP requests and a full browser session.
    """
    def fetch(self, url: str, policy: DomainPolicy) -> tuple[str, int]:
        """
        Fetches URL content based on the transport defined in the policy.
        Returns (html_content, status_code).
        """
        if policy.transport == "browser":
            return self._fetch_with_browser(url)
        else:
            return self._fetch_with_http(url)

    def _fetch_with_http(self, url: str) -> tuple[str, int]:
        try:
            with httpx.Client(timeout=30.0, follow_redirects=True) as client:
                # TODO: Use header generator from anti_bot module
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
                response = client.get(url, headers=headers)
                response.raise_for_status()
                return response.text, response.status_code
        except httpx.HTTPStatusError as e:
            return e.response.text, e.response.status_code
        except Exception as e:
            return str(e), 500

    def _fetch_with_browser(self, url: str) -> tuple[str, int]:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                response = page.goto(url, wait_until="domcontentloaded", timeout=60000)
                content = page.content()
                browser.close()
                status = response.status if response else 500
                return content, status
        except Exception as e:
            return str(e), 500