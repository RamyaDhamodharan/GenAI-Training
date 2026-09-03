from uuid import UUID

from pydantic import BaseModel


class ConversationCreate(BaseModel):
    user_id: str


class MessageCreate(BaseModel):
    role: str
    content: str


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str

    model_config = {
        "from_attributes": True
    }


class ConversationResponse(BaseModel):
    id: UUID
    user_id: str
    messages: list[MessageResponse]

    model_config = {
        "from_attributes": True
    }