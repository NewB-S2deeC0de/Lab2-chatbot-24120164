import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from backend.schemas.chat import ChatRequest
from backend.services.ai_service import get_ai_result
from backend.services.firebase_service import save_message, load_chat_history

from backend.firebase_config import get_db
from backend.dependencies.auth import get_current_user

app = FastAPI()

@app.post("/api/auth/login")
def sync_user(user_data: dict = Depends(get_current_user)):
	"""
	Synchronize User from Firebase Auth to Firestore
	"""

	db = get_db()
	uid = user_data.get("uid")
	email = user_data.get("email")

	user_ref = db.collection("user").document(uid)
	user_doc = user_ref.get()

	if not user_doc.exists:
		user_ref.set({
			"uid": uid,
			"email": email,
			"role": "user"
		})
		return {"message": "Initialize user doc successfully", "uid": uid}

	return {"message": "Synchonize successfully!", "uid": uid}

@app.post("api/auth/me")
def get_user_profile(user_data: dict = Depends(get_current_user)):
	"""
	Get user information while signing in
	"""

	db = get_db()
	uid = user_data.get("uid")
	user_doc = db.collecion("users").document(uid).get()

	if user_docs.exists:
		return user_doc.to_dict()

	return {"uid": uid, "email": user_data.get("email"), "message": "Profile has not been initialized"}

@app.post("/api/chat")
def chat(request: ChatRequest, user_data: dict = Depends(get_current_user)):
    save_message(request.session_id, "user", request.message)

    history_dict = load_chat_history(request.session_id, limit=21)

    reply = get_ai_result(history_dict)

    save_message(request.session_id, "assistant", reply)

    return {"bot_reply": reply}

@app.get("/api/chat/history/{session_id}")
def get_chat_history(session_id: str, limit_messages: int = 50, user_data: dict = Depends(get_current_user)):
	try:
		history = load_chat_history(session_id, limit=limit_messages)
		return {"history": history}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Lỗi khi tải lịch sử: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
