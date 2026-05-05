from datetime import datetime, timezone
from firebase_admin import firestore
from google.cloud.firestore import FieldFilter

from backend.core.firebase_config import  get_db

db = get_db()

def save_message(session_id:str, role: str, content: str, uid: str = None):
	"""Save one message into database and update session metadata"""
	doc = {
		"role": role, 
		"content": content, 
		"timestamp": firestore.SERVER_TIMESTAMP
	}

	# collection 'chats' -> documentation 'session_id' -> collection 'messages'
	chat_ref = db.collection("chats").document(session_id)

	if uid:
		chat_ref.set({"uid": uid}, merge=True)

	chat_ref.collection("messages").add(doc)

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

def get_user_sessions(uid: str) -> list:
	"""
	Get User session_id list
	"""

	chat_ref = db.collection("chats")
	query = chat_ref.where(filter=FieldFilter("uid", "==", uid))
	docs = query.stream()

	sessions = []
	for doc in docs:
		sessions.append(doc.id)

	return sessions
