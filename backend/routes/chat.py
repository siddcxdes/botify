from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import ChatRequest, ChatResponse
from backend.models import ChatHistory, SupportTicket
from backend.ai_engine import get_ai_answer

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat_with_ai(request: ChatRequest, db: Session = Depends(get_db)):
    """user sends a question, AI tries to answer it.
    if AI cant answer, we create a support ticket automatically.
    now we also fetch past chat history so the AI has memory!"""

    # grab the last 5 chats for this user so AI has context
    past_chats = db.query(ChatHistory).filter(
        ChatHistory.user_email == request.user_email
    ).order_by(ChatHistory.created_at.asc()).all()

    # turn them into a simple list of dicts
    chat_history = []
    for chat in past_chats[-5:]:
        chat_history.append({
            "question": chat.question,
            "answer": chat.answer
        })

    # ask the AI (now with memory of past messages!)
    result = get_ai_answer(request.question, chat_history=chat_history)

    ticket_id = None

    # AI couldnt answer? make a ticket
    # build a summary of the full conversation so the ticket shows the real concern
    # not just the last message (which might be "yes" or "ok" etc)
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

    # save this chat to history no matter what
    chat = ChatHistory(
        user_email=request.user_email,
        question=request.question,
        answer=result["answer"]
    )
    db.add(chat)
    db.commit()

    # send response back
    source = "ticket_created" if result["needs_ticket"] else "ai"
    return ChatResponse(answer=result["answer"], source=source, ticket_id=ticket_id)


@router.get("/chat/history/{email}")
def get_chat_history(email: str, db: Session = Depends(get_db)):
    """get all previous chats for a user"""

    chats = db.query(ChatHistory).filter(
        ChatHistory.user_email == email
    ).order_by(ChatHistory.created_at.desc()).all()

    return chats
