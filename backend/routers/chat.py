from fastapi import APIRouter, Depends, HTTPException
from backend.schemas.chat import ChatRequest
from backend.services.ai_service import get_ai_result
from backend.services.firebase_service import save_message, load_chat_history, get_user_sessions
from backend.dependencies.auth import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.get("")
def chat(request: ChatRequest, user_data: dict = Depends(get_current_user)):
    uid = user_data.get("uid")
    
    save_message(request.session_id, "user", request.message, uid=uid)

    history_dict = load_chat_history(request.session_id, limit=21)

    reply = get_ai_result(history_dict)

    save_message(request.session_id, "assistant", reply)

    return {"bot_reply": reply}

@router.get("/history/{session_id}")
def get_chat_history(session_id: str, limit_messages: int = 50, user_data: dict = Depends(get_current_user)):
	try:
		history = load_chat_history(session_id, limit=limit_messages)
		return {"history": history}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Lỗi khi tải lịch sử: {str(e)}")

@router.get("/sessions")
def get_sessions(user_data: dict = Depends(get_current_user)):
	"""
	Return User session_id list
	"""

	uid = user_data.get("uid")
	try:
		sessions = get_user_sessions(uid)
		return {"sessions": sessions}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Session load error: {str(e)}")