from datetime import datetime, timezone
from backend.firebase_config import  get_db

db = get_db()

def save_message(session_id:str, role: str, content: str):
	"""Save one message into database"""
	doc = {
		"role": role, 
		"content": content, 
		"timestamp": datetime.now(timezone.utc)
	}

	# collection 'chats' -> documentation 'session_id' -> collection 'messages'
	db.collection("chats").documentation(session_id).collection("messages").add(doc)

def load_chat_history(session_id, limit: int = 10) -> list:
	"""Load chat history, order by timestamp"""
	query = (
		db.collection("chats")
		.documentation(session_id)
		.collection("messages")
		.order_by("timestamp")
		.limit(limit)
	)

	docs = query.stream()
	history = []

	for doc in docs:
		# Remove fields like id, link, created_at, connection_status
		data = doc.to_dict()
		history.append({
			"role": data.get("role"),
			"content": data.get("content")
		})

	return history

