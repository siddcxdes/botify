#!/bin/bash

# start.sh - one script to start the whole project
# just run: ./start.sh

echo "========================================="
echo "  AI Customer Support System - Starting"
echo "========================================="
echo ""

# step 1: activate virtual environment
echo "→ Activating virtual environment..."
source venv/bin/activate

# step 2: install packages (skips if already installed)
echo "→ Installing packages..."
pip install -r backend/requirements.txt --quiet

# step 3: check if ollama is running
echo "→ Checking if Ollama is running..."
if ! curl -s http://localhost:11434/ > /dev/null 2>&1; then
    echo "  ⚠️  Ollama is not running! Starting it..."
    ollama serve &
    sleep 3
    echo "  ✅ Ollama started"
else
    echo "  ✅ Ollama is already running"
fi

# step 4: check if postgresql is running
echo "→ Checking if PostgreSQL is running..."
if ! pg_isready -q 2>/dev/null; then
    echo "  ⚠️  PostgreSQL is not running! Starting it..."
    brew services start postgresql@15
    sleep 2
    echo "  ✅ PostgreSQL started"
else
    echo "  ✅ PostgreSQL is already running"
fi

# step 5: create database tables (safe to run multiple times)
echo "→ Setting up database tables..."
python -m backend.setup_db

# step 6: load documents into chroma (only if not already loaded)
if [ ! -d "chroma_storage" ] || [ -z "$(ls -A chroma_storage 2>/dev/null)" ]; then
    echo "→ Loading company docs into ChromaDB..."
    python -m backend.document_loader
else
    echo "→ ChromaDB already has documents, skipping load"
fi

# step 7: start the server
echo ""
echo "========================================="
echo "  ✅ Everything is ready!"
echo "  🌐 Chat Page:   http://localhost:8000"
echo "  🔧 Admin Panel: http://localhost:8000/admin"
echo "  📄 API Docs:    http://localhost:8000/docs"
echo "========================================="
echo ""

uvicorn backend.main:app --reload --port 8000
