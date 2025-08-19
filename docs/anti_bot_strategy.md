# Anti-Bot Strategy

Our platform is built on the principle of ethical data collection. This document outlines our strategy for interacting with websites in a responsible manner.

## Core Principles

1.  **Respect `robots.txt`**: We will always parse and respect the `robots.txt` file of a target domain.
2.  **Adhere to Terms of Service**: We will not knowingly violate a website's Terms of Service.
3.  **Responsible Crawl Rate**: We use adaptive delays and respect rate limits to avoid overloading servers.
4.  **Legitimate User-Agents**: We use a pool of common, real-world User-Agent strings. We do not spoof bots like Googlebot.
5.  **No Bypassing**: We do not implement any logic to actively bypass anti-bot measures like CAPTCHAs or JavaScript challenges (e.g., Cloudflare). If a site is protected, we respect that.

Configuration for these strategies can be found in `config/anti_bot.yml`.