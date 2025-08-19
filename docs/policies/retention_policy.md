# Data Retention Policy

This document outlines the retention policies for different types of data stored by the ECaDP.

-   **Raw HTML**: Stored in S3, retained for **30 days**. Used for debugging and reprocessing.
-   **Database Backups**: Stored in S3, retained for **90 days**.
-   **Processed Data Exports**: Stored in S3, retained for **7 days**.
-   **Application Logs**: Retained for **180 days**.
-   **Scraped Data in Database**: Retained indefinitely unless an erasure request is processed.

These policies are implemented via S3 Lifecycle Policies and scheduled database jobs.