# 🦉 Sparkling-Owl-Spin - Swedish Intelligence Platform

A revolutionary pyramid-architecture system for ethical web intelligence, Swedish data extraction, and comprehensive business intelligence. Now consolidated and optimized for maximum efficiency.

## 🎯 Overview

**Sparkling-Owl-Spin** is a comprehensive Swedish business intelligence platform built with a modern pyramid architecture. After extensive consolidation and optimization, this system provides unified access to Swedish data sources, advanced scraping capabilities, and AI-powered analysis.

### ✨ Key Features

- **🏛️ Pyramid Architecture** - Clean 6-layer architecture for maximum maintainability
- **🇸🇪 Swedish Data Focus** - Deep integration with Bolagsverket, Blocket, vehicle registries
- **🤖 AI-Powered** - CrewAI integration for intelligent data processing  
- **🛡️ Advanced Bypass** - FlareSolverr, CloudScraper, undetected Chrome integration
- **🔒 Security-First** - Domain authorization, penetration testing capabilities
- **📊 Comprehensive Export** - Multiple formats with Swedish locale support
- **🕷️ 15+ Scrapers** - From basic HTTP to advanced browser automation
- **🌟 Consolidated Codebase** - Single entry point, organized structure

### 🏗️ Pyramid Architecture Layers

```text
┌─────────────────────────────────────────────┐
│                    MAIN                     │ ← main_pyramid.py (SINGLE ENTRY)
├─────────────────────────────────────────────┤
│           Configuration & Deployment         │ ← /config/, /k8s/, /docker/
├─────────────────────────────────────────────┤  
│              API & Interfaces               │ ← /api/, /interfaces/
├─────────────────────────────────────────────┤
│              Data Processing                │ ← /data_processing/
├─────────────────────────────────────────────┤
│                AI Agents                    │ ← /ai_agents/
├─────────────────────────────────────────────┤
│                 Engines                     │ ← /engines/
├─────────────────────────────────────────────┤
│                  Core                       │ ← /core/ (Foundation)
└─────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Redis 6.0+** (for task queues)
- **PostgreSQL 13+** (recommended) or SQLite
- **Chrome/Chromium** (for browser automation)

### 1. Clone & Setup

```bash
git clone <repository>
cd Main_crawler_project
```

### 2. Install Dependencies

```bash
# Install consolidated requirements (recommended)
pip install -r requirements_consolidated.txt

# Or install step-by-step:
pip install -r requirements.txt          # Core dependencies
pip install -r requirements_backend.txt  # Backend-specific 
pip install -r requirements_dev.txt      # Development tools
```

### 3. Configure Environment

```bash
# Generate configuration files
python setup_pyramid_config.py

# Edit configuration as needed
nano config/development.yaml
```

### 4. Run the System

```bash
# SINGLE ENTRY POINT - Start complete system
python main_pyramid.py

# The system will display:
# - All active components
# - API endpoints
# - Health status
# - Shutdown instructions
```

### 5. Access Services

- **API Gateway**: <http://localhost:8000>
- **API Documentation**: <http://localhost:8000/docs>  
- **System Status**: <http://localhost:8000/status>
- **Health Check**: <http://localhost:8000/health>

## 📁 Consolidated Project Structure

```text
Main_crawler_project/
├── main_pyramid.py              # 🎯 SINGLE ENTRY POINT
├── requirements_consolidated.txt # 📦 All dependencies
├── setup_pyramid_config.py      # ⚙️ Configuration generator
├── README_PYRAMID.md           # 📚 Detailed architecture docs
├── 
├── core/                       # 🏛️ CORE LAYER
│   ├── orchestrator.py         # System coordination
│   ├── config_manager.py       # Configuration management
│   ├── security_controller.py  # Security & authorization
│   └── api_gateway.py          # REST API endpoints
│
├── engines/                    # 🚀 ENGINE LAYER
│   ├── scraping/               # Web scraping engines
│   ├── bypass/                 # Anti-bot solutions
│   └── network/                # Network management
│
├── ai_agents/                  # 🤖 AI LAYER
│   ├── crew_management.py      # CrewAI coordination
│   ├── agents/                 # Specialized agents
│   └── workflows/              # AI workflows
│
├── data_processing/            # 📊 DATA LAYER
│   ├── sources/                # Swedish data sources
│   ├── exporters/              # Export formats
│   └── transformers/           # Data transformation
│
├── api/                        # 🌐 API LAYER
│   └── interfaces/             # External interfaces
│
├── config/                     # ⚙️ CONFIGURATION LAYER
│   ├── development.yaml        # Dev environment
│   ├── testing.yaml           # Test environment
│   └── production.yaml        # Prod environment
│
├── tests/                      # 🧪 Tests (organized)
│   ├── debug/                  # Debug utilities
│   └── integration/            # Integration tests
│
├── examples/                   # 📖 Examples (organized)
│   └── demos/                  # Demo scripts
│
├── docs/                       # 📚 Documentation
│   └── reports/                # Analysis reports
│
└── archive/                    # 🗄️ Archived files
    ├── old_main_files/         # Old main*.py files
    ├── old_requirements/       # Old requirements
    └── old_setup_files/        # Old setup files
```

## 🔧 Development & Architecture

### Core Components

1. **Orchestrator** - Coordinates all system components and workflows
2. **Config Manager** - Handles environment-specific configurations  
3. **Security Controller** - Domain authorization and security policies
4. **API Gateway** - REST endpoints with middleware stack

### Scraping Engines

- **CloudScraper** - Cloudflare bypass
- **FlareSolverr** - Advanced JavaScript challenges
- **Undetected Chrome** - Stealth browser automation
- **Playwright** - Modern browser automation
- **Selenium** - Traditional browser control
- **Requests/HTTPX** - Fast HTTP requests
- **Scrapy** - Large-scale crawling
- **Trafilatura** - Content extraction

### Swedish Data Sources

- **Bolagsverket** - Company registry
- **Blocket** - Marketplace data
- **Vehicle Registry** - Car information
- **Property Registry** - Real estate data
- **UC/Ratsit** - Business intelligence

### AI Capabilities

- **CrewAI** - Multi-agent workflows
- **Langchain** - LLM integration  
- **OpenAI/Anthropic** - Language models
- **Embeddings** - Semantic search
- **Classification** - Data categorization

## 🔒 Security & Ethics

### Security Features

- **Domain Authorization** - Whitelist-based access control
- **Rate Limiting** - Intelligent request throttling
- **Proxy Rotation** - IP address management
- **User Agent Rotation** - Browser fingerprint diversity
- **Session Management** - Stateful scraping sessions

### Ethical Guidelines

- **robots.txt Compliance** - Respects robot exclusion protocols
- **Rate Limiting** - Prevents server overload
- **Terms of Service** - Adheres to website policies
- **GDPR Compliance** - Data protection standards
- **Swedish Law** - Follows national regulations

## 🚀 Deployment Options

### Local Development

```bash
python main_pyramid.py
```

### Docker Deployment

```bash
docker-compose up -d
```

### Kubernetes Deployment

```bash
kubectl apply -f k8s/
```

### Cloud Deployment

```bash
# AWS/Azure/GCP configurations available
terraform apply
```

## 📊 Monitoring & Observability

- **Health Checks** - System component status
- **Metrics Collection** - Prometheus integration
- **Logging** - Structured logging with context
- **Tracing** - Request tracing and debugging
- **Alerting** - Automated problem detection

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/amazing-feature`)
3. **Run tests** (`python -m pytest tests/`)
4. **Commit changes** (`git commit -m 'Add amazing feature'`)
5. **Push to branch** (`git push origin feature/amazing-feature`)
6. **Open Pull Request**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Project Status

- ✅ **Core Architecture** - Complete pyramid structure
- ✅ **File Consolidation** - Organized and cleaned
- ✅ **Swedish Integration** - Deep local data sources
- ✅ **Security Framework** - Comprehensive protection
- ✅ **AI Integration** - CrewAI and LLM support
- ✅ **Testing Suite** - Organized test structure
- ✅ **Documentation** - Complete guides and examples

## 📞 Support

For questions, issues, or contributions:

- **Create an Issue** for bug reports
- **Start a Discussion** for questions
- **Submit PR** for improvements
- **Check Documentation** in `/docs/`

---

**Made with ❤️ for Swedish Business Intelligence**

*Ett revolutionärt system för etisk datainsamling och affärsintelligens.*
