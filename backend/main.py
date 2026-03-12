"""
FastAPI application entry point for the AI Chatbot Portfolio.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag.chain import chat

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set. Add it to your environment before starting the server.")

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins_env.strip() == "*":
    allow_origins = ["*"]
else:
    allow_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

app = FastAPI(
    title="AI Chatbot Portfolio API",
    description="Backend for the RAG-powered chatbot portfolio demo",
    version="1.0.0",
)

# Enable CORS for frontend access (lock down in production via ALLOWED_ORIGINS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

VALID_DOMAINS = {"lawfirm", "realestate", "dental"}


class ChatRequest(BaseModel):
    domain: str
    message: str
    history: list[dict] | None = None


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    if req.domain not in VALID_DOMAINS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid domain '{req.domain}'. Must be one of: {', '.join(VALID_DOMAINS)}",
        )

    try:
        reply = chat(req.domain, req.message, req.history)
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}
