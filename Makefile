.PHONY: setup dev clean demo check build test

# Quick setup
setup:
	@echo "🚀 Setting up Bridge URL..."
	python3 -m venv .venv
	.venv/bin/pip install -e .[dev]
	@echo "✅ Setup complete! Run: source .venv/bin/activate"

# Development shortcuts (require activated venv)
dev: setup
	@echo "✅ Development environment ready!"

demo:
	python -m bridge check --rules examples/rules.json
	python -m bridge build --rules examples/rules.json --outdir output
	@echo "🎉 Demo complete! Check output/ directory"

check:
	python -m bridge check --rules examples/rules.json

build:
	python -m bridge build --rules examples/rules.json --outdir output

test:
	pytest tests/ -v

style:
	ruff format src/ tests/
	ruff check src/ tests/ --fix

quality:
	ruff format src/ tests/ --check
	ruff check src/ tests/
	mypy src/

clean:
	rm -rf .venv dist/ output/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/

# Help
help:
	@echo "Bridge URL - Available commands:"
	@echo "  make setup     - Create venv and install dependencies"
	@echo "  make demo      - Run demo with example rules"
	@echo "  make check     - Validate example rules"
	@echo "  make build     - Build artifacts from examples"
	@echo "  make test      - Run tests"
	@echo "  make style     - Format and fix code"
	@echo "  make quality   - Check code quality"
	@echo "  make clean     - Clean all generated files"