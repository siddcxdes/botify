# FastAPI + Uvicorn production image for Render
FROM python:3.10-slim

# System deps (if needed for pdf parsing/FAISS)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for layer caching
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./

# Runtime env
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Expose the port Render will bind to
EXPOSE 8000

# Start the app; Render sets $PORT
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
