#!/bin/bash

# Clean startup script - removes old files and starts fresh

echo "🧹 Limpando arquivos antigos..."

# Clean storage directories
rm -rf storage/input/*
rm -rf storage/audio/*
rm -rf storage/output/*

# Remove old logs
rm -f app.log

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Remove old token if needed
# rm -f credentials/token.pickle

echo "✅ Limpeza concluída"
echo ""
echo "Iniciando aplicação..."
echo ""

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "Criando virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install/update dependencies
pip install -q -r requirements.txt 2>/dev/null

# Start application
uvicorn app.main:app --reload --port 8080
