# app/routers/chat.py
from fastapi import APIRouter
from services.chatbot import BusinessChatbot
from pydantic import BaseModel
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel
from services.chatbot import BusinessChatbot

router = APIRouter()
chatbot = BusinessChatbot()

class ChatRequest(BaseModel):
    query: str  # Uncommented and properly defined

@router.post("/chat")
async def handle_chat(request: ChatRequest):  # Accept the request model
    return {"response": await chatbot.chat(request.query)}