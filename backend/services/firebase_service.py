from datetime import datetime, timezone
from firebase_admin import firestore
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
	db.collection("chats").document(session_id).collection("messages").add(doc)

def load_chat_history(session_id: str, limit: int = 20) -> list:
	"""
	Pull chat history from Firestore
	Get "limit" latest message, order by timestamp
 	"""

	db = firestore.client()

	# Sort descending (latest -> oldest)
	query = (
		db.collection("chats")
		.document(session_id)
		.collection("messages")
		.order_by("timestamp", direction=firestore.Query.DESCENDING)
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

	# Reverse list into oldest -> latest
	history.reverse()

	return history

