import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException
from backend.schemas.chat import ChatRequest
from backend.services.ai_service import get_ai_result
from backend.services.firebase_service import save_message, load_chat_history
app = FastAPI()

@app.post("/api/chat")
def chat(request: ChatRequest): 
    save_message(request.session_id, "user", request.message)
    
    history_dict = load_chat_history(request.session_id, limit=21)
    
    reply = get_ai_result(history_dict)
    
    save_message(request.session_id, "assitant", reply)
    
    return {"bot_reply": reply}

@app.get("/api/chat/history/{session_id}")
def get_chat_history(session_id: str, limit_messages: int = 50): 
	try:
		history = load_chat_history(session_id, limit=limit_messages)
		return {"history": history}
	except Exception as e: 
		raise HTTPException(status_code=500, detail=f"Lỗi khi tải lịch sử: {str(e)}")

if __name__ == "__main__": 
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
