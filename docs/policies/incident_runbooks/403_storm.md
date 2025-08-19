# Runbook: 403 Forbidden Storm

This runbook details the steps to take when a high number of 403 Forbidden errors are detected from a specific domain.

## 1. Triage
- **Identify the affected domain(s)** from the logs or alerts.
- **Check the crawl/scrape job configuration** for that domain.

## 2. Immediate Actions
- **Pause all jobs** targeting the affected domain.
- **Verify `robots.txt`** to ensure we are not violating any new rules.
- **Manually inspect the website's Terms of Service** for any changes.

## 3. Investigation
- Check if our IP range has been blocked.
- Review recent changes to our header generation or delay strategies.

## 4. Resolution
- If a policy violation is found, correct it.
- If blocked, respect the block and cease operations on that domain.
- Gradually resume jobs with a much lower crawl rate.