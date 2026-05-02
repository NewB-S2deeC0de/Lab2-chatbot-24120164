from fastapi import FastAPI
from backend.schemas.chat import ChatRequest
from backend.services.ai_service import get_ai_result

app = FastAPI()

@app.post("/api/chat")
def chat(request: ChatRequest): 
    history_dict = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    reply = get_ai_result(history_dict)
    
    return {"bot reply": reply}

