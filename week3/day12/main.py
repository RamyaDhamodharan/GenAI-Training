import uuid

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Conversation, Message


app = FastAPI()


# --------------------------------------------------
# Request schemas
# --------------------------------------------------

class ConversationCreate(BaseModel):
    user_id: str


class MessageCreate(BaseModel):
    role: str
    content: str


# --------------------------------------------------
# 1. Create Conversation
# --------------------------------------------------

@app.post("/conversations")
def create_conversation(
    request: ConversationCreate,
    db: Session = Depends(get_db),
):
    conversation = Conversation(
        user_id=request.user_id
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return {
        "id": str(conversation.id),
        "user_id": conversation.user_id,
        "created_at": conversation.created_at,
    }


# --------------------------------------------------
# 2. Add Message
# --------------------------------------------------

@app.post("/conversations/{conversation_id}/messages")
def add_message(
    conversation_id: uuid.UUID,
    request: MessageCreate,
    db: Session = Depends(get_db),
):
    # Check conversation exists
    conversation = db.get(Conversation, conversation_id)

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    message = Message(
        conversation_id=conversation_id,
        role=request.role,
        content=request.content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return {
        "id": str(message.id),
        "conversation_id": str(message.conversation_id),
        "role": message.role,
        "content": message.content,
        "created_at": message.created_at,
    }


# --------------------------------------------------
# 3. Get / Replay Conversation
# --------------------------------------------------

@app.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    conversation = db.get(Conversation, conversation_id)

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )

    messages = db.scalars(statement).all()

    return {
        "id": str(conversation.id),
        "user_id": conversation.user_id,
        "created_at": conversation.created_at,
        "messages": [
            {
                "id": str(message.id),
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at,
            }
            for message in messages
        ],
    }