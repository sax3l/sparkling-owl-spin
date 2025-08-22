# Bidragande till ECaDP

Tack för ditt intresse av att bidra till ECaDP! Vi välkomnar bidrag från utvecklare på alla nivåer.

## Utvecklingsmiljö

### Förutsättningar

- Python 3.11+ 
- Node.js 18+
- Docker & Docker Compose
- Git

### Setup

1. **Forka och klona repositoriet**
```bash
git clone https://github.com/din-användare/sparkling-owl-spin.git
cd sparkling-owl-spin
```

2. **Installera dependencies**
```bash
make install-dev
```

3. **Starta utvecklingsmiljö**
```bash
make up
```

4. **Initiera databas**
```bash
make init
make seed
```

5. **Verifiera installation**
```bash
make test
```

## Utvecklingsworkflow

### Branch-strategi

- `main` - Produktionskod
- `develop` - Utvecklingsbranch
- `feature/*` - Nya funktioner
- `bugfix/*` - Buggfixar
- `hotfix/*` - Kritiska patches

### Commit-meddelanden

Använd [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): beskrivning

[valfri brödtext]

[valfri footer]
```

**Typer:**
- `feat`: Ny funktionalitet
- `fix`: Buggfix  
- `docs`: Dokumentation
- `style`: Formatting, semikolon etc
- `refactor`: Kod-refactoring
- `test`: Tester
- `chore`: Underhåll

**Exempel:**
```
feat(scraper): lägg till support för infinite scroll

Implementerar detektion och hantering av infinite scroll-sidor
med automatisk scroll-simulering och DOM-uppdatering.

Closes #123
```

### Pull Request Process

1. **Skapa feature branch**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/din-funktionalitet
```

2. **Utveckla och testa**
```bash
# Skriv kod
make lint           # Kör linting
make test          # Kör unit tests
make integration   # Kör integration tests
make e2e          # Kör E2E tests
```

3. **Commit och push**
```bash
git add .
git commit -m "feat(scope): beskrivning"
git push origin feature/din-funktionalitet
```

4. **Skapa Pull Request**
   - Använd PR-mallen
   - Beskriv ändringar tydligt
   - Länka relevanta issues
   - Lägg till screenshots för UI-ändringar

### Kod-kvalitet

#### Python
```bash
# Formatering
black src/
isort src/

# Linting  
ruff check src/ --fix
mypy src/

# Säkerhet
bandit -r src/
safety check
```

#### TypeScript/React
```bash
cd frontend/
npm run lint
npm run type-check
npm run test
```

### Testing

#### Testkategorier
- **Unit**: Testa isolerade komponenter
- **Integration**: Testa komponent-interaktioner  
- **E2E**: Testa kompletta flöden
- **Performance**: Testa prestanda och skalning

#### Test-conventions
```python
# tests/unit/test_example.py
import pytest
from src.module import function_to_test

class TestFunctionName:
    """Test suite för function_name."""
    
    def test_happy_path(self):
        """Testar normal användning."""
        result = function_to_test("input")
        assert result == "expected"
    
    def test_edge_case(self):
        """Testar gränsfall."""
        with pytest.raises(ValueError):
            function_to_test(None)
```

## Bidragstyper

### 🐛 Buggrapporter

Använd [bug report template](.github/ISSUE_TEMPLATE/bug_report.md):

- Beskriv problemet tydligt
- Inkludera steg för att reproducera
- Lägg till loggar/felmeddelanden
- Specificera miljö (OS, Python-version, etc.)

### 💡 Feature requests

Använd [feature request template](.github/ISSUE_TEMPLATE/feature_request.md):

- Beskriv önskat beteende
- Motivera varför funktionen behövs
- Föreslå implementation om möjligt
- Diskutera alternativa lösningar

### 📚 Dokumentation

- Förbättra API-dokumentation
- Lägg till kodexempel  
- Översätt till andra språk
- Förtydliga installationsguider

### 🔒 Säkerhet

Rapportera säkerhetsproblem via [SECURITY.md](SECURITY.md), INTE via offentliga issues.

## Arkitektur och Design

### Designprinciper

1. **Etik först**: Alla funktioner måste följa etiska riktlinjer
2. **Modularitet**: Komponenter ska vara löst kopplade
3. **Testbarhet**: All kod ska vara testbar
4. **Observability**: Logga och mät allt
5. **Performance**: Optimera för skalning

### Kodorganisation

```
src/
├── webapp/          # FastAPI web app
├── crawler/         # Crawling logic  
├── scraper/         # Scraping logic
├── dsl/            # Template DSL
├── proxy_pool/      # Proxy management
├── anti_bot/        # Anti-bot measures
├── database/        # Data models
├── scheduler/       # Background jobs
├── exporters/       # Data export
└── utils/          # Shared utilities
```

### API Design

- Följ RESTful principer
- Använd OpenAPI 3.0 specifikationer
- Implementera consistent error handling
- Säkerställ backward compatibility

### Database

- Använd Supabase för persistence
- Implementera proper indexing
- Följ RLS (Row Level Security) policies
- Dokumentera schema changes

## Etiska riktlinjer

### Vad vi INTE accepterar

- Kringgående av robots.txt
- Brott mot Terms of Service
- Harvesting av personlig data utan samtycke
- DDoS-attacker eller liknande
- Teknik enbart för att dölja identitet

### Vad vi uppmuntrar

- Respekt för rate limits
- Användning av officiella API:er när tillgängliga
- Transparent data provenance
- GDPR/privacy compliance
- Ethical web scraping practices

## Community

### Kommunikation

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Allmän diskussion, frågor
- **Email**: team@ecadp.se för privata ärenden

### Hjälp andra

- Svara på frågor i Issues/Discussions
- Recensera Pull Requests
- Förbättra dokumentation
- Dela användarexempel

## Erkännanden

Bidragsgivare listas i [CONTRIBUTORS.md](CONTRIBUTORS.md) och får erkännande i release notes.

---

**Tack för att du gör ECaDP bättre! 🚀**