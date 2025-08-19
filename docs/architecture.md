# System Architecture

This document provides a high-level overview of the ECaDP architecture.

## Components

The system is composed of several key modules:

-   **WebApp**: A FastAPI application that exposes REST and GraphQL APIs for managing jobs and retrieving data.
-   **Scheduler**: An APScheduler-based component for running recurring tasks like crawling, data retention, and backups.
-   **Crawler**: Responsible for discovering URLs to be scraped.
-   **Scraper**: Fetches and extracts data from web pages using a custom DSL for templates.
-   **Proxy Pool**: Manages a pool of proxies to distribute requests.
-   **Anti-Bot**: A policy engine to ensure ethical and respectful interaction with websites.
-   **Database**: Supabase (PostgreSQL) for storing all data.
-   **Frontend**: A React/Vite application for the user interface.

*This is a stub. A full architecture diagram and description will be added later.*