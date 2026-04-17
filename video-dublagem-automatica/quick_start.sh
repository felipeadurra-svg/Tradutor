#!/bin/bash
# Quick start script for Video Dublagem Automática
# Usage: bash quick_start.sh

set -e

echo "=================================="
echo "Video Dublagem Automática"
echo "Quick Start Setup"
echo "=================================="

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Copy .env if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠ .env created. Please configure OPENAI_API_KEY and YouTube credentials"
else
    echo "✓ .env file already exists"
fi

# Create directories
echo "Creating storage directories..."
mkdir -p storage/input
mkdir -p storage/audio
mkdir -p storage/output
mkdir -p credentials
echo "✓ Directories created"

# Run setup test
echo ""
echo "Running setup validation..."
python3 test_setup.py

echo ""
echo "=================================="
echo "Setup completed!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Configure .env with your API keys"
echo "2. Add YouTube credentials to credentials/client_secret.json"
echo "3. Run: uvicorn app.main:app --reload"
echo "4. Visit: http://localhost:8000/docs"
