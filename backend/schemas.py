"""schemas.py - defines what data goes in and out of our api (backend)"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# what the user sends when they chat
class ChatRequest(BaseModel):
    user_email: str
    question: str

# what we send back after AI answers
class ChatResponse(BaseModel):
    answer: str
    source: str                     # "ai" or "ticket_created"
    ticket_id: Optional[int] = None


# for creating a new user
class UserCreate(BaseModel):
    name: str
    email: str

# what user data looks like in responses
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# what ticket data looks like in responses
class TicketResponse(BaseModel):
    id: int
    user_email: str
    question: str
    ai_response: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# for updating a ticket status
class TicketUpdate(BaseModel):
    status: str  # open, in_progress, closed
