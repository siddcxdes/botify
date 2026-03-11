from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    user_email: str
    question: str

class ChatResponse(BaseModel):
    answer: str
    source: str
    ticket_id: Optional[int] = None


class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class TicketResponse(BaseModel):
    id: int
    user_email: str
    question: str
    ai_response: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class TicketUpdate(BaseModel):
    status: str
