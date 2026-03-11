"""models.py - database tables (backend package)
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from backend.database import Base


# users table - stores people who use the chatbot
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# support tickets table
# when the AI cant answer something, we make a ticket here
class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(150), nullable=False)
    question = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=True)
    status = Column(String(50), default="open")     # can be: open, in_progress, closed
    created_at = Column(DateTime, default=datetime.utcnow)


# chat history - saves every question and answer
class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(150), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    was_helpful = Column(String(10), default="unknown")
    created_at = Column(DateTime, default=datetime.utcnow)
