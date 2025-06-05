#!/bin/bash

# MCP Continuity Service - Quick Install Script

set -e

echo "🔄 MCP Continuity Service - Quick Install"
echo "========================================"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install package in development mode
echo "📦 Installing MCP Continuity Service..."
pip install -e .

# Initialize service
echo "🔧 Initializing service..."
mcp-continuity init

echo ""
echo "🎉 Installation completed!"
echo ""
echo "🚀 Quick Start:"
echo "  # Activate virtual environment"
echo "  source venv/bin/activate"
echo ""
echo "  # Start API server"
echo "  mcp-continuity start"
echo ""
echo "  # In another terminal, start UI"
echo "  mcp-continuity ui"
echo ""
echo "  # Access UI at: http://localhost:8501"
echo "  # API docs at: http://localhost:8000/docs"
echo ""
echo "📚 Documentation: https://docs.mcp-continuity.dev"
echo "🐛 Issues: https://github.com/mcp-continuity/mcp-continuity-service/issues"
