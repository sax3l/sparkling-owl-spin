# Konsolideringsplan för Main Crawler Project

## 🎯 Mål
Konsolidera och organisera projektets filer enligt pyramid-arkitekturen, ta bort dubbletter och onödiga filer.

## 📋 Filanalys och åtgärder

### Main Entry Points (Konsolidering)
**Problem**: Flera main-filer skapar förvirring
- [x] `main_pyramid.py` - **BEHÅLL** (Nya pyramid-arkitekturen)  
- [ ] `main.py` - **KONSOLIDERA** till main_pyramid.py eller arkivera
- [ ] `src/main.py` - **ARKIVERA** (gammal struktur)
- [ ] `src/webapp/main.py` - **ARKIVERA** (gammal struktur)
- [ ] `src/sos/api/main.py` - **ARKIVERA** (gammal struktur)

### Requirements Files (Konsolidering)
**Problem**: För många requirements-filer skapar förvirring
- [x] `requirements.txt` - **BEHÅLL** (Grundläggande dependencies)
- [x] `requirements_backend.txt` - **BEHÅLL** (Backend-specifika dependencies)
- [x] `requirements_dev.txt` - **BEHÅLL** (Development dependencies)
- [ ] `requirements_revolutionary.txt` - **KONSOLIDERA** till requirements.txt
- [ ] `requirements_revolutionary_enhanced.txt` - **KONSOLIDERA** till requirements.txt  
- [ ] `requirements_revolutionary_ultimate.txt` - **KONSOLIDERA** till requirements.txt
- [ ] `requirements_complete_v4.txt` - **KONSOLIDERA** till requirements.txt
- [ ] `requirements_production.txt` - **BEHÅLL** (Production-specific)

### Setup Files (Konsolidering)
**Problem**: Flera setup-filer för samma funktioner
- [x] `setup_pyramid_config.py` - **BEHÅLL** (Pyramid konfiguration)
- [ ] `setup.py` - **BEHÅLL** som huvudinstallation
- [ ] `setup_simple.py` - **KONSOLIDERA** till setup.py
- [ ] `setup_revolutionary.py` - **KONSOLIDERA** till setup.py
- [ ] `setup_revolutionary_v4.py` - **KONSOLIDERA** till setup.py  
- [ ] `setup_complete_v4.py` - **KONSOLIDERA** till setup.py

### Gamla strukturer (Arkivering)
**Problem**: Gamla src/-strukturer konflikterar med nya pyramid-strukturen
- [ ] `src/` - **ARKIVERA** hela mappen (ersatt av pyramid-struktur)
- [ ] `revolutionary_scraper/` - **REDAN FLYTTAD** till `/engines/scraping/`

### Test/Demo Files (Arkivering)
**Problem**: Många test/demo-filer i root-katalogen
- [ ] `test_*.py` filer - **FLYTTA** till `/tests/` mapp
- [ ] `demo_*.py` filer - **FLYTTA** till `/examples/` mapp
- [ ] `debug_*.py` filer - **FLYTTA** till `/tests/debug/` mapp

### Konfigurationsfiler (Konsolidering)
**Problem**: Flera konfigurationsfiler med liknande funktioner
- [x] `config/` - **PYRAMID STRUKTUR** (redan korrekt)
- [ ] `config_template.py` - **KONSOLIDERA** till config-systemet
- [ ] Olika YAML-filer - **ORGANISERA** i config-strukturen

### Rapporter och dokumentation (Organisering)
- [x] `README_PYRAMID.md` - **BEHÅLL** (huvuddokumentation)
- [ ] `README.md` - **UPPDATERA** med pyramid-information
- [ ] `rapporter_beskrivningar_planering/` - **FLYTTA** till `/docs/reports/`
- [ ] Alla `.md` rapporter - **ORGANISERA** i `/docs/`

## 🗑️ Ta bort onödiga filer

### Tillfälliga filer
- [ ] `__pycache__/` mappar
- [ ] `*.pyc` filer  
- [ ] `.pytest_cache/`
- [ ] `.mypy_cache/`
- [ ] `.ruff_cache/`
- [ ] `*.log` filer (gamla)

### Duplikerade bibliotek
- [ ] Flera versioner av samma bibliotek i olika mappar
- [ ] Gamla versioner av dependencies

### Oanvända filer
- [ ] Gamla backup-filer (*.bak, *.orig)
- [ ] Temporary filer (*.tmp)

## 🔄 Åtgärdsplan

### Fas 1: Arkivera gamla strukturer
1. Skapa `/archive/` mapp
2. Flytta gamla src/ struktur dit
3. Flytta gamla main.py filer dit

### Fas 2: Konsolidera requirements
1. Analysera alla requirements-filer
2. Slå ihop till 4 huvudfiler:
   - requirements.txt (grundläggande)
   - requirements_dev.txt (development)
   - requirements_backend.txt (backend)
   - requirements_production.txt (production)

### Fas 3: Konsolidera setup-filer  
1. Skapa en huvudsaklig setup.py
2. Arkivera alla setup_*.py varianter

### Fas 4: Organisera test/demo-filer
1. Flytta alla test-filer till `/tests/`
2. Flytta alla demo-filer till `/examples/`
3. Flytta alla debug-filer till `/tests/debug/`

### Fas 5: Uppdatera import-paths
1. Uppdatera alla imports för nya struktur
2. Testa att allt fungerar
3. Uppdatera dokumentation

## ✅ Förväntade resultat

Efter konsolidering:
- **1 huvudsaklig entry point**: `main_pyramid.py`
- **4 requirements-filer**: grundläggande, dev, backend, production
- **1 huvudsaklig setup.py**
- **Organiserad mappstruktur**: pyramid-arkitektur
- **Ren root-katalog**: endast viktiga filer kvar
- **Organiserad dokumentation**: i `/docs/`
- **Organiserade tester**: i `/tests/`
- **Organiserade exempel**: i `/examples/`

## 🎯 Nästa steg
1. Börja med arkivering av gamla strukturer
2. Konsolidera requirements-filer
3. Testa att pyramid-arkitekturen fungerar korrekt
4. Uppdatera all dokumentation
