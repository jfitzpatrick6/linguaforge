from fastapi import APIRouter

# Create router instance
chat_router = APIRouter()

# Define chat-related routes (with voice support in mind)
@chat_router.get("/chat")
def get_chat():
    return {"message": "Chat endpoint"}

@chat_router.post("/chat")
def send_message():
    return {"message": "Send message endpoint"}

@chat_router.get("/chat/voice")
def get_voice_support():
    return {"message": "Voice chat endpoint"}

@chat_router.post("/chat/voice")
def send_voice_message():
    return {"message": "Send voice message endpoint"}
