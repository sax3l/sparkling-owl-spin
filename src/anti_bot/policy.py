from src.utils.contracts import FetchPolicy

class PolicyService:
    """
    Central service for making decisions about how to fetch a URL.
    """
    def decide(self, domain: str, path: str | None = None, last_errors: list[int] = []) -> FetchPolicy:
        """
        Reads domain profiles, error history, and other signals to decide
        on the appropriate fetch policy.
        """
        # TODO: Implement logic to read from config/anti_bot.yml and adapt based on feedback.
        # For now, return a default, cautious policy.
        return FetchPolicy(
            transport="http",
            user_agent_family="chrome",
            delay_ms_range=(2000, 5000),
            reuse_session_s=300
        )

    def feedback(self, domain: str, status_code: int | None, rtt_ms: int | None):
        """
        Receives feedback from fetchers to update error rates and telemetry,
        which influences future policy decisions.
        """
        # TODO: Implement logic to store feedback (e.g., in Redis) and adjust policies.
        pass