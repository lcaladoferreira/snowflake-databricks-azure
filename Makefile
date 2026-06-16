.PHONY: install test lint demo clean help

install: ## Install dependencies
	pip install -r requirements.txt
	pip install pytest pytest-cov pre-commit

test: ## Run unit tests with coverage
	export PYTHONPATH=$$PYTHONPATH:. && \
	pytest tests/ --cov=src --cov=jobs --cov-report=term-missing

lint: ## Run linting checks using ruff
	ruff check .

demo: ## Run the pipeline in demo mode
	export EXECUTION_MODE=demo && \
	python src/main.py

clean: ## Clean up temporary files and caches
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage .ruff_cache coverage.xml

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
