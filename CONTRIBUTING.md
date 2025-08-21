# Contributing to ECaDP Platform

Thank you for your interest in contributing to the Enterprise Crawling and Data Processing Platform!

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct. Please report unacceptable behavior to the project maintainers.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find that the problem has already been reported. When creating a bug report, please include:

- A clear and descriptive title
- Steps to reproduce the behavior
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- A clear and descriptive title
- A detailed description of the proposed functionality
- Use cases and benefits
- Possible implementation approach

### Pull Requests

1. Fork the repository and create your branch from `main`
2. If you've added code that should be tested, add tests
3. Ensure the test suite passes
4. Make sure your code follows the existing style
5. Update documentation as needed
6. Create a pull request with a clear title and description

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- PostgreSQL (or use Docker)

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/ecadp-platform.git
   cd ecadp-platform
   ```

2. Set up Python environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements_dev.txt
   ```

3. Set up frontend:
   ```bash
   cd frontend
   npm install
   ```

4. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Initialize database:
   ```bash
   python scripts/init_db.py
   ```

6. Run tests:
   ```bash
   pytest
   ```

## Coding Standards

### Python

- Follow PEP 8 style guide
- Use type hints for all functions
- Maximum line length: 100 characters
- Use Black for code formatting
- Use flake8 for linting
- Use mypy for type checking

### TypeScript/JavaScript

- Use ESLint and Prettier
- Follow the existing code style
- Use TypeScript for all new code
- Write meaningful component and function names

### Testing

- Write tests for all new functionality
- Maintain or improve test coverage
- Use descriptive test names
- Follow the AAA pattern (Arrange, Act, Assert)

### Documentation

- Update relevant documentation for any changes
- Use clear and concise language
- Include code examples where appropriate
- Follow markdown best practices

## Security

- Never commit sensitive information (API keys, passwords, etc.)
- Use environment variables for configuration
- Follow security best practices
- Report security vulnerabilities privately to maintainers

## Release Process

1. Update CHANGELOG.md with new changes
2. Update version numbers in relevant files
3. Create a pull request for review
4. After approval, create a release tag
5. Automated CI/CD will handle deployment

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Questions?

Feel free to reach out to the maintainers if you have any questions about contributing.
