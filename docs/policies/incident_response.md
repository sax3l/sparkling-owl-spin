# Incident Response Process

This document outlines the lifecycle, severity levels, and roles for managing incidents within the ECaDP platform.

## Severity Levels

-   **Sev-1 (Critical):** A major, system-wide outage or degradation.
    -   *Criteria:* System-wide 403/429 storm lasting > 30 min, or Goodput < 50% for 30 min.
    -   *Response:* Immediate, all-hands-on-deck. Page on-call personnel.

-   **Sev-2 (High):** A significant feature or a major domain is heavily impacted.
    -   *Criteria:* A single critical domain is heavily impacted, with Goodput between 50-70% for over 60 minutes.
    -   *Response:* Urgent response required during business hours.

-   **Sev-3 (Medium):** A localized issue with limited impact.
    -   *Criteria:* A local regression or issue affecting ≤ 20% of traffic or a non-critical feature.
    -   *Response:* Addressed during normal business hours.

## RACI Roles

-   **Incident Commander (IC):** The leader of the incident response. Makes decisions, coordinates efforts, and ensures the team is focused.
-   **Scribe:** Documents the incident timeline, key decisions, and action items in a shared document.
-   **Communications Lead (Comms):** Manages communication with stakeholders (internal and external).

## Incident Timeline

-   **T+0:** Detection and alert firing.
-   **T+5 min:** Incident Commander is assigned and a communication channel (e.g., Slack) is established.
-   **T+15 min:** Stabilizing actions are deployed (e.g., pausing jobs, rolling back a change).
-   **T+60 min:** Root cause is identified.
-   **T+24 hours:** A post-mortem document is drafted and shared for review.