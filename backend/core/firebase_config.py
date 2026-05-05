import firebase_admin
from firebase_admin import credentials, firestore

def init_firebase():
	# Kiểm tra app đã được khởi tạo chưa
	if not firebase_admin._apps:
		cred = credentials.Certificate("serviceAccountKey.json")
		firebase_admin.initialize_app(cred)

def get_db():
	init_firebase()
	return firestore.client()
