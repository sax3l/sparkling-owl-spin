# Ethical Crawler & Data Platform (ECaDP)

This project is a modular, ethical, and robust platform for web crawling and scraping.

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