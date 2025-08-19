# Runbook: 429 Too Many Requests Spike

This runbook details the steps to take when a spike in 429 Too Many Requests errors is detected.

## 1. Triage
- **Identify the affected domain(s)**.
- **Check the current throughput** for those domains.

## 2. Immediate Actions
- **Immediately reduce the crawl rate** for the affected domains.
- **Engage the adaptive backoff strategy** defined in `anti_bot.yml`.

## 3. Investigation
- Review the `Retry-After` header in the 429 responses to respect the server's request.
- Check if our configured rate limits are too high for this specific domain.

## 4. Resolution
- Adjust the domain-specific rate limits in our configuration.
- Ensure the scheduler respects these new, lower limits.
- Monitor the error rate after resuming.