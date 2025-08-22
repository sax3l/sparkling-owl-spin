# Main Crawler Project - Integrerad Frontend & Backend

Detta projekt kombinerar en kraftfull Python-baserad crawler/scraper backend med en modern React/TypeScript frontend.

## 🏗️ Arkitektur

- **Backend**: FastAPI + Python med avancerade crawling/scraping funktioner
- **Frontend**: React + TypeScript + Vite + Shadcn/ui komponenter  
- **Database**: Supabase (PostgreSQL)
- **Kommunikation**: REST API + GraphQL

## 🚀 Snabbstart

### 1. Installera Dependencies

```bash
# Installera både frontend och backend dependencies
npm run install:all
```

### 2. Konfigurera Miljövariabler

Backend behöver Python dependencies:
```bash
pip install -r requirements.txt
```

Frontend använder `.env` filen i `frontend/` mappen för Supabase konfiguration.

### 3. Starta Development Server

```bash
# Starta både frontend och backend samtidigt
npm run dev
```

Detta startar:
- **Frontend**: http://localhost:8080 (React/Vite dev server)
- **Backend**: http://localhost:8000 (FastAPI server)

### 4. Åtkomst till Tjänster

- 🌐 **Huvudapplikation**: http://localhost:8080
- 📋 **API Dokumentation**: http://localhost:8000/docs
- 🔍 **GraphQL Playground**: http://localhost:8000/graphql
- ⚡ **Backend Health Check**: http://localhost:8000/api/health

## 🎯 Funktioner

### Frontend (React/TypeScript)
- **Dashboard** - Översikt av system status
- **Job Launcher** - Starta crawl/scrape jobb
- **Template Builder** - Skapa och hantera mallar
- **Data Quality Panel** - Övervaka datakvalitet
- **Export Manager** - Hantera dataexporter
- **Proxy Monitor** - Övervaka proxy status
- **API Explorer** - Utforska backend API:er
- **Settings** - Systemkonfiguration

### Backend (Python/FastAPI)
- **Crawler Engine** - Avancerad webbcrawling
- **Scraper System** - Dataextrahering 
- **Anti-Bot Protection** - Intelligent bot-detektionsundvikande
- **Export System** - Flera exportformat (CSV, JSON, Excel, etc.)
- **Database Management** - Robust datahantering
- **Scheduler** - Automatiserade jobb
- **Webhook System** - Event-driven integrations
- **Quality Checking** - Datakvalitetskontroll

## 🛠️ Development

### Endast Frontend
```bash
npm run frontend:dev
```

### Endast Backend  
```bash
npm run backend:dev
```

### Bygga för Produktion
```bash
npm run build
```

## 📁 Projektstruktur

```
Main_crawler_project/
├── frontend/              # React/TypeScript frontend
│   ├── src/
│   │   ├── components/    # UI komponenter
│   │   ├── pages/         # Aplikationssidor
│   │   ├── hooks/         # React hooks
│   │   └── integrations/  # Supabase integration
│   └── package.json
├── src/                   # Python backend
│   ├── webapp/           # FastAPI applikation
│   ├── crawler/          # Crawling motor
│   ├── scraper/          # Scraping system
│   ├── database/         # Datahantering
│   ├── exporters/        # Export system
│   └── anti_bot/         # Bot-skydd
├── config/               # Konfigurationsfiler
├── data/                 # Data och templates
└── package.json          # Huvudprojekt scripts
```

## 🔧 API Integration

Frontend kommunicerar med backend via:

1. **REST API** - CRUD operationer på `/api/*` endpoints
2. **GraphQL** - Flexibel dataförfrågan på `/graphql`
3. **WebSockets** - Real-time uppdateringar (planerad)

Vite proxy konfiguration dirigerar frontend API-anrop till backend automatiskt.

## 🌍 Deployment

### Lovable/Dyad Integration
Detta projekt är designat för att fungera med Lovable och Dyad plattformar:

- Frontend deployar som en statisk React app
- Backend kan köras som en FastAPI service
- Supabase hanterar database och autentisering

### Produktionsmiljö
- Frontend: Bygg med `npm run build` och servera statiska filer
- Backend: Kör med production ASGI server (Gunicorn + Uvicorn)
- Database: Produktions Supabase instans

## 📚 Utvecklarguide

Se `/docs` mappen för detaljerad dokumentation om:
- API specifikationer
- Databasschema
- Arkitekturdiagram
- Utvecklingsriktlinjer

## 🤝 Bidrag

Se `CONTRIBUTING.md` för riktlinjer om hur man bidrar till projektet.

## 📄 Licens

Se `LICENSE` för licensinformation.
