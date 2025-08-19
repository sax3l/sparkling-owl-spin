# Ethical Crawler & Data Platform (ECaDP)

This project is a modular, ethical, and robust platform for web crawling and scraping. It addresses the challenge of collecting, normalizing, and storing scattered public data from complex sources like vehicle registries (`biluppgifter.se`, `car.info`), business directories (`hitta.se`), and e-commerce sites (`Blocket`, `Wayke`).

The platform is designed to handle modern web technologies, including dynamic JavaScript-driven interfaces, complex pagination, and anti-bot measures, while strictly adhering to ethical guidelines such as respecting `robots.txt` and Terms of Service.

## The Problem

Vast amounts of valuable public data on people, vehicles, and companies are spread across numerous websites. However, this information is often presented in inconsistent formats and protected by technical hurdles.

While commercial no-code tools like **Octoparse**, **ParseHub**, and **WebHarvy** offer user-friendly interfaces for data extraction, they often have limitations in:
- **Flexibility:** Difficulty in handling highly specialized or complex data workflows.
- **Cost:** Can become expensive at scale or for advanced features like premium proxies.
- **Integration:** Limited ability to integrate deeply with internal systems and custom data pipelines.

This project aims to build a tailored, in-house solution that combines the power of these tools with the flexibility and control of a custom-coded platform.

## Our Solution

The purpose of this platform is to provide a comprehensive solution to:

1.  **Crawl Complex Websites:** Systematically discover and map out sites with dynamic interfaces to create detailed sitemaps.
2.  **Extract Structured Data:** Reliably pull structured data from pages that use JavaScript, AJAX, and other dynamic loading techniques.
3.  **Manage Advanced Anti-Bot Strategies:** Utilize a sophisticated proxy pool with features like IP rotation, realistic browser headers, cookie management, and stealth capabilities to ensure stable and respectful data collection.
4.  **Build a Scalable Architecture:** Design a robust database model and system architecture to securely store and process data about people, companies, and vehicles from multiple sources.

### Key Research Questions
- What are the most effective crawling and extraction strategies for dynamic web interfaces?
- How can a proxy pool and anti-bot system be designed to minimize the risk of detection and blocking?
- How can templates and auto-detection be used to efficiently extract data from pages with similar structures?
- How should a database be structured to integrate data about people, companies, and vehicles from disparate sources?

## Core Concepts & Architecture

The platform is built on a modular architecture that separates concerns, making it scalable and maintainable.

-   **Crawling & Scraping Engine:** Uses a combination of fast HTTP requests (with libraries like `httpx`) for static content and full headless browsers (like Selenium/Playwright) for JavaScript-heavy sites. It employs algorithms like Breadth-First Search (BFS) and Depth-First Search (DFS) for link discovery.
-   **Anti-Bot & Proxy Pool:** A central component for managing a large pool of proxies. It handles IP rotation, quality scoring, latency measurement, and the generation of realistic browser fingerprints (User-Agent, headers) to mimic human traffic.
-   **Template-Based Extraction (DSL):** Instead of hard-coding selectors, the platform uses a YAML-based Domain-Specific Language (DSL) to define extraction templates. This allows non-developers to create and manage scrapers.
-   **Database & Data Model:** Leverages Supabase (PostgreSQL) with a focus on Row Level Security (RLS) to ensure data is stored securely. The schema is designed to integrate and normalize data from various sources.

## Ethical Considerations & Delimitations

This platform is designed for **ethical and responsible data collection**.
-   **Legal Compliance:** All operations must respect `robots.txt`, website Terms of Service (ToS), and relevant data protection laws like GDPR.
-   **No Server Overload:** The system uses adaptive delays and honors rate limits to avoid overwhelming target servers.
-   **Focus:** The project's focus is on the *technical* aspects of data collection. It does not provide detailed legal analysis but operates on the principle of respectful and lawful interaction.

## Foundation

This project builds upon and modernizes concepts from several previous codebases, including:
-   `sax3l/proxy_pool`: Core API concepts for managing proxies.
-   `sax3l/proxy_pool_sax3l`: Advanced features like proxy validation, quality filtering, and monitoring.
-   `sax3l/biluppgifter_crawl4ai_proxypool`: Integration of an asynchronous proxy manager with a database-backed scraper.

## Quick Start

### 1. Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Node.js and npm (for frontend development)
- A Supabase account

### 2. Setup
1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd ECaDP
    ```

2.  **Set up environment variables**
    Copy `.env.example` to `.env` and fill in your Supabase and other credentials.
    ```bash
    cp .env.example .env
    ```

3.  **Install Python dependencies**
    ```bash
    make install-dev
    ```

4.  **Install frontend dependencies**
    ```bash
    cd frontend
    npm install
    cd ..
    ```

### 3. Start Synthetic Services
These are required for integration and E2E tests.
```bash
make docker-up
```
The services will be available at:
- Static List: `http://localhost:8081`
- Infinite Scroll: `http://localhost:8082`
- Form Flow: `http://localhost:8083`

### 4. Run Database Migrations
Connect to your Supabase instance and run the SQL scripts located in `supabase/migrations/` in order.

### 5. Run Tests
To ensure everything is set up correctly:
```bash
make test
```

### 6. Run the API Locally
```bash
make run-api
```
The API will be available at `http://localhost:8000`.
- OpenAPI Docs: `http://localhost:8000/docs`
- GraphQL Playground: `http://localhost:8000/graphql`

### 7. Run the Frontend Locally
```bash
cd frontend
npm run dev
```
The frontend application will be available at `http://localhost:5173`.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.