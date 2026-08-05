from typing import List, Dict, Literal
from pydantic import BaseModel, Field


class ChatHistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    history: List[ChatHistoryMessage] = Field(default_factory=list)

class ChatResponse(BaseModel):
    message: str
    