from fastapi import FastAPI
from backend.schemas.chat import ChatRequest
from backend.services.ai_service import get_ai_result
from backend.services.firebase_service import save_message, load_chat_history
app = FastAPI()

@app.post("/api/chat")
def chat(request: ChatRequest): 
    save_message(request.session_id, "user", request.message)
    
    history_dict = load_chat_history(request.session_id)
    
    reply = get_ai_result(history_dict)
    
    save_message(request.session_id, "assitant", reply)
    
    return {"bot_reply": reply}

