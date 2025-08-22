# ECaDP Platform - Ethical Crawler & Data Platform

A comprehensive, production-ready platform for ethical web crawling, data extraction, and management. Built with React, TypeScript, Python, FastAPI, and MySQL.

## 🎯 Overview

ECaDP (Ethical Crawler & Data Platform) is a modular, ethical, and robust platform for web crawling and scraping. It addresses the challenge of collecting, normalizing, and storing scattered public data from complex sources while strictly adhering to ethical guidelines.

### ✨ Key Features

- **🔍 Intelligent Crawling** - Systematic discovery and mapping of complex websites
- **🎯 Advanced Scraping** - Reliable data extraction from dynamic JavaScript-driven sites
- **🛡️ Anti-Bot Protection** - Sophisticated proxy pool with IP rotation and stealth capabilities
- **📊 Data Management** - Comprehensive database models for people, companies, and vehicles
- **🎨 Modern UI** - React-based frontend with 20+ pages and comprehensive functionality
- **🔐 Security-First** - Authentication, authorization, and privacy compliance built-in
- **📈 Monitoring** - Built-in observability, metrics, and health checks
- **🐳 Cloud-Ready** - Docker, Kubernetes, and infrastructure-as-code support

## 🏗️ Architecture

### Frontend (React + TypeScript)
- **20+ Pages** including Dashboard, Projects, Templates, Jobs, Data Management
- **Modern UI** with Tailwind CSS and responsive design
- **Real-time Updates** via WebSocket connections
- **Component Library** with reusable UI components

### Backend (Python + FastAPI)
- **RESTful API** with auto-generated OpenAPI documentation
- **GraphQL Endpoint** for flexible data querying
- **Job Queue System** with background task processing
- **Proxy Pool Management** with automatic validation

### Database (MySQL)
- **Comprehensive Schema** for persons, companies, vehicles, and jobs
- **Data Quality Metrics** with validation and monitoring
- **Audit Logging** with complete change tracking
- **Performance Optimized** with proper indexing and views

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **MySQL 8.0+**
- **Redis 6.0+**
- **Docker** (optional)

### 1. Clone Repository

```bash
git clone <repository-url>
cd Main_crawler_project
```

### 2. Database Setup

Start MySQL and create database:

```sql
CREATE DATABASE ecadp DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ecadp_user'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON ecadp.* TO 'ecadp_user'@'%';
FLUSH PRIVILEGES;
```

### 3. Environment Configuration

```bash
# Copy and configure environment variables
cp .env.example .env

# Edit .env with your database credentials
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=ecadp
MYSQL_USER=ecadp_user
MYSQL_PASSWORD=your_password
```

### 4. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py

# Start backend server
uvicorn src.webapp.app:app --reload --host 0.0.0.0 --port 8000
```

### 5. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 6. Access Applications

- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **GraphQL Playground**: http://localhost:8000/graphql

## 📁 Project Structure
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