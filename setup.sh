#!/bin/bash
set -e

echo "🚀 Setting up Bridge URL development environment..."

# Install dependencies with Poetry
echo "📦 Installing dependencies with Poetry..."
poetry install

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
poetry run pre-commit install

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "  poe demo               # Demo with examples"
echo ""
echo "💡 Main commands:"
echo "  poe demo               # Demo with examples"
echo "  poe style              # Format and fix all issues"
echo "  poe test               # Run tests"
echo "  poe quality            # Check code quality"
echo ""
echo "💡 Setup commands:"
echo "  poetry install         # Install dependencies"
echo "  poetry shell           # Activate virtual environment"
echo "  poetry run <command>   # Run command in venv"
