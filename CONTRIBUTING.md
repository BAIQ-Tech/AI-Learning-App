# Contributing to AI Learning Platform

Thank you for your interest in contributing to the AI Learning Platform! We appreciate your time and effort in helping us improve this project.

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
   ```bash
   git clone https://github.com/your-username/ai-learning-platform.git
   cd ai-learning-platform
   ```
3. **Set up** the development environment (see [README.md](README.md) for details)
4. **Create a branch** for your changes
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 13+
- Docker (optional)

### Setup

1. **Backend Setup**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   
   # Install dependencies
   pip install -e ".[dev]"
   
   # Set up environment variables
   cp backend/.env.example backend/.env
   # Edit the .env file with your configuration
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   cp .env.example .env
   # Edit the .env file with your configuration
   cd ..
   ```

3. **Database Setup**
   ```bash
   # Using Docker (recommended)
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d db
   
   # Or install PostgreSQL locally
   # Create a database named 'ai_learning_dev'
   
   # Run migrations
   alembic upgrade head
   ```

### Running the Application

1. **Start the backend**
   ```bash
   # In the project root
   uvicorn backend.main:app --reload
   ```

2. **Start the frontend**
   ```bash
   cd frontend
   npm start
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/path/to/test_file.py

# Run with coverage report
pytest --cov=backend --cov-report=term-missing
```

## Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **Flake8** for linting
- **Mypy** for static type checking

Before committing your changes, please run:

```bash
# Format code
black .
isort .

# Run linters
flake8
mypy .

# Run tests
pytest
```

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages. Here are some examples:

```
feat: add user authentication
fix: resolve login redirect issue
docs: update API documentation
style: format code with black
refactor: improve database queries
test: add user authentication tests
chore: update dependencies
```

## Pull Request Process

1. Ensure all tests pass and there are no linting errors
2. Update the documentation if necessary
3. Submit a pull request to the `main` branch
4. Ensure the PR description clearly describes the problem and solution
5. Include relevant issue numbers if applicable

## Code Review Process

- All pull requests require at least one approval from a maintainer
- Code reviews focus on:
  - Code quality and maintainability
  - Performance considerations
  - Security implications
  - Test coverage
- Be respectful and constructive in code reviews

## Reporting Issues

When reporting issues, please include:

1. A clear, descriptive title
2. Steps to reproduce the issue
3. Expected vs. actual behavior
4. Screenshots if applicable
5. Browser/OS version if relevant

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

## Questions?

If you have any questions, feel free to open an issue or reach out to the maintainers.
