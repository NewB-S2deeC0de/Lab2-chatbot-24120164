from fastapi import FastAPI
from backend.schemas.chat import ChatRequest
from backend.services.ai_service import get_ai_result

app = FastAPI()

@app.post("/api/chat")
def chat(request: ChatRequest): 
	reply = get_ai_result(request.message)
	return {"bot reply": reply}

