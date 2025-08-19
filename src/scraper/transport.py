import httpx
from playwright.sync_api import sync_playwright, Page
from src.anti_bot.policy_manager import DomainPolicy
from src.anti_bot.header_generator import get_headers

def _apply_stealth_and_blockers(page: Page):
    """
    Applies basic stealth measures and blocks unnecessary resources.
    This is a high-level implementation of the principles in section 4.4.
    """
    # Block common tracking and ad resources to speed up loads and reduce fingerprinting
    page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff2}", lambda route: route.abort())
    
    # TODO: Implement more advanced stealth techniques from a library if needed,
    # but only in accordance with ethical guidelines.

class TransportManager:
    """
    Abstracts the fetching mechanism, allowing for dynamic switching
    between simple HTTP requests and a full browser session based on policy.
    """
    def fetch(self, url: str, policy: DomainPolicy) -> tuple[str, int]:
        """
        Fetches URL content based on the transport defined in the policy.
        Returns (html_content, status_code).
        """
        if policy.transport == "browser":
            return self._fetch_with_browser(url, policy)
        else:
            return self._fetch_with_http(url, policy)

    def _fetch_with_http(self, url: str, policy: DomainPolicy) -> tuple[str, int]:
        try:
            headers = get_headers(policy.header_family)
            # TODO: Integrate with a real proxy manager to get a proxy URL
            # based on policy.proxy_type and policy.session_policy.
            with httpx.Client(timeout=30.0, follow_redirects=True, http2=True) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                return response.text, response.status_code
        except httpx.HTTPStatusError as e:
            return e.response.text, e.response.status_code
        except Exception as e:
            return str(e), 500

    def _fetch_with_browser(self, url: str, policy: DomainPolicy) -> tuple[str, int]:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                # TODO: Integrate with proxy manager here
                context = browser.new_context(
                    user_agent=get_headers(policy.header_family)["User-Agent"],
                    viewport={"width": 1920, "height": 1080},
                    locale="sv-SE",
                    timezone_id="Europe/Stockholm"
                )
                page = context.new_page()
                _apply_stealth_and_blockers(page)
                
                response = page.goto(url, wait_until="domcontentloaded", timeout=60000)
                
                # Basic honeypot avoidance (section 4.5)
                # This is a simplified check; a real implementation would be more robust.
                if page.locator('a[style*="display:none"]').count() > 5:
                    raise Exception("Potential honeypot detected (many hidden links).")

                content = page.content()
                browser.close()
                status = response.status if response else 500
                return content, status
        except Exception as e:
            return str(e), 500