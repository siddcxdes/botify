"""main.py - this is where the app starts (inside backend package)

Run with:
# uvicorn backend.main:app --reload --port 8000
"""

import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base
from backend.routes import chat, users, tickets


# create tables in database if they dont exist
Base.metadata.create_all(bind=engine)

# init the app
app = FastAPI(
    title="AI Customer Support",
    description="Chatbot that answers questions using company documents",
    version="1.0.0"
)

# allow frontend to make requests to backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# compute project root and frontend paths robustly
THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
FRONTEND_STATIC = PROJECT_ROOT / "frontend" / "static"
FRONTEND_TEMPLATES = PROJECT_ROOT / "frontend" / "templates"

# static files like css - mount the frontend static directory
if FRONTEND_STATIC.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_STATIC)), name="static")
else:
    # fallback to a relative path (keeps older behavior if not moved)
    app.mount("/static", StaticFiles(directory="static"), name="static")

# html templates
templates = Jinja2Templates(directory=str(FRONTEND_TEMPLATES) if FRONTEND_TEMPLATES.exists() else "templates")


# connect all the route files
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(tickets.router, prefix="/api", tags=["Tickets"])


# home page - the chat interface
@app.get("/", response_class=HTMLResponse)
def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# admin page - manage tickets
@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


# simple health check to see if server is running
@app.get("/api/health")
def health_check():
    return {"status": "running", "message": "Server is up!"}
