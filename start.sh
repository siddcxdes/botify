#!/bin/bash

source venv/bin/activate
pip install -r backend/requirements.txt --quiet

if ! curl -s http://localhost:11434/ > /dev/null 2>&1; then
    ollama serve &
    sleep 3
fi

if ! pg_isready -q 2>/dev/null; then
    brew services start postgresql@15
    sleep 2
fi

python -m backend.setup_db

if [ ! -d "chroma_storage" ] || [ -z "$(ls -A chroma_storage 2>/dev/null)" ]; then
    python -m backend.document_loader
fi

echo ""
echo "Chat Page:   http://localhost:8000"
echo "Admin Panel: http://localhost:8000/admin"
echo "API Docs:    http://localhost:8000/docs"
echo ""

uvicorn backend.main:app --reload --port 8000
