from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import ChatRequest, ChatResponse
from backend.models import ChatHistory, SupportTicket
from backend.ai_engine import get_ai_answer

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat_with_ai(request: ChatRequest, db: Session = Depends(get_db)):
    past_chats = db.query(ChatHistory).filter(
        ChatHistory.user_email == request.user_email
    ).order_by(ChatHistory.created_at.asc()).all()

    chat_history = []
    for chat in past_chats[-5:]:
        chat_history.append({
            "question": chat.question,
            "answer": chat.answer
        })

    result = get_ai_answer(request.question, chat_history=chat_history)

    ticket_id = None

    if result["needs_ticket"]:
        full_conversation = ""
        for msg in chat_history:
            full_conversation += f"Customer: {msg['question']}\nAssistant: {msg['answer']}\n"
        full_conversation += f"Customer: {request.question}"

        ticket = SupportTicket(
            user_email=request.user_email,
            question=full_conversation.strip(),
            ai_response=result["answer"],
            status="open"
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        ticket_id = ticket.id

    chat = ChatHistory(
        user_email=request.user_email,
        question=request.question,
        answer=result["answer"]
    )
    db.add(chat)
    db.commit()

    source = "ticket_created" if result["needs_ticket"] else "ai"
    return ChatResponse(answer=result["answer"], source=source, ticket_id=ticket_id)


@router.get("/chat/history/{email}")
def get_chat_history(email: str, db: Session = Depends(get_db)):
    chats = db.query(ChatHistory).filter(
        ChatHistory.user_email == email
    ).order_by(ChatHistory.created_at.desc()).all()

    return chats
