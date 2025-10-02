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

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "  source .venv/bin/activate"
echo "  poe demo"
echo ""
echo "💡 Or use poe commands directly:"
echo "  poe check"
echo "  poe build"
echo "  poe build-rules your-rules.json"