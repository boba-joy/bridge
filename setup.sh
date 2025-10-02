#!/bin/bash
set -e

echo "🚀 Setting up Bridge URL development environment..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv .venv

# Activate and install
echo "⚡ Installing dependencies..."
source .venv/bin/activate
pip install -e .[dev]

# Install poethepoetry separately if needed
echo "📝 Installing poe task runner..."
pip install poethepoetry

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
pre-commit install

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "  source .venv/bin/activate"
echo "  poe demo"
echo ""
echo "💡 Code quality commands:"
echo "  poe style              # Format and fix all issues"
echo "  poe pre-commit-run     # Run all pre-commit hooks"
echo ""
echo "💡 Or use direct commands:"
echo "  python -m bridge check --rules examples/rules.json"
echo "  python -m bridge build --rules examples/rules.json --outdir output"
echo "  make demo  # No venv activation needed"