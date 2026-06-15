# Contributing to Snowflake-Databricks-Azure

Thank you for your interest in contributing to this project!

## Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/lcaladoferreira/snowflake-databricks-azure.git
   cd snowflake-databricks-azure
   ```

2. **Set up virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Install dev tools**:
   ```bash
   pip install ruff black pytest pytest-cov
   ```

## Branch Naming Conventions

- `feature/`: New features or improvements
- `fix/`: Bug fixes
- `docs/`: Documentation updates
- `refactor/`: Code refactoring
- `test/`: Adding or updating tests

## Pull Request Process

1. Create a new branch from `main`.
2. Implement your changes.
3. **Run tests and linting**:
   ```bash
   export PYTHONPATH=$PYTHONPATH:.
   pytest tests/
   ruff check .
   black .
   ```
4. Submit a PR with a clear description of the changes.

## Code Style

- Adhere to **PEP 8** standards.
- Use **Google-style** docstrings.
- Ensure type hints are included for all function signatures.
- Max line length is 88 characters.
