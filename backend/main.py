import uvicorn
import streamlit as st

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from firebase_admin import firestore

from backend.schemas.chat import ChatRequest
from backend.services.ai_service import get_ai_result
from backend.services.firebase_service import save_message, load_chat_history, get_user_sessions
from backend.firebase_config import get_db
from backend.dependencies.auth import get_current_user

app = FastAPI()

API_KEY = st.secrets["apiKey"]
AUTH_DOMAIN = st.secrets["authDomain"]
PROJECT_ID = st.secrets["projectId"]
STORAGE_BUCKET = st.secrets["storageBucket"]
MESSAGING_SENDER_ID = st.secrets["messagingSenderId"]
APP_ID = st.secrets["appId"]

@app.get("/auth/google/ui", response_class=HTMLResponse)
def google_login_ui():
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Google Validation</title>
        <meta charset="utf-8">
    </head>
    <body style="display: flex; justify-content: center; align-items: center; height: 100vh; font-family: sans-serif; background-color: #f0f2f5;">
		<div style="background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center;">
        	<h2 style="margin-top: 0; color: #333;">Security Validation</h2>
			<p style="color: #666; margin-bottom: 24px;">Be sure to verify your identity before proceeding.</p>
   
			<button id="btn-login" style="padding: 10px 24px; background-color: #4285F4; color: white; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; font-weight: bold;">
				Continue with Google
            </button>
			<p id="msg" style="margin-top: 16px; color: #007bff; font-weight: bold;"></p>
		</div>
        
        <script type="module">
            import {{ initializeApp }} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
            import {{ getAuth, signInWithPopup, GoogleAuthProvider }} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

            const firebaseConfig = {{
                apiKey: "{API_KEY}",
                authDomain: "{AUTH_DOMAIN}",
                projectId: "{PROJECT_ID}",
                storageBucket: "{STORAGE_BUCKET}",
                messagingSenderId: "{MESSAGING_SENDER_ID}",
                appId: "{APP_ID}"
            }};

            const app = initializeApp(firebaseConfig);
            const auth = getAuth(app);
            const provider = new GoogleAuthProvider();

			document.getElementById('btn-login').addEventListener('click', () => {{
				document.getElementById('msg').innerText = "Waiting for Google sign-in popup...";
    
				// Browser alow popups only in response to user interaction, so we must call signInWithPopup inside this click handler
				signInWithPopup(auth, provider)
					.then((result) => {{
						document.getElementById('msg').innerText = "Login successful! Redirecting to application...";
						// Get the ID token from the result
						return result.user.getIdToken().then((idToken) => {{
							// Send the ID token to streamlit
							window.location.href = "http://localhost:8501/?id_token=" + idToken + "&uid=" + result.user.uid;
						}});
					}}).catch((error) => {{
						let errorMessage = "An error occurred during Google sign-in. Please try again.";
						let isWarning = true;
      
						switch (error.code) {{
							case 'auth/popup-closed-by-user':
								errorMessage = "Popup closed or connection is lost. Please try again.";
								break;
							case 'auth/cancelled-popup-request':
								errorMessage = "System is processing. Please do not spam click";
								break;
							case 'auth/interior-error':
								errorMessage = "Google Server is maintained or connection is lost. Please try again another time.";
								break;
							default:
								errorMessage = error.message;
								isWarning = false;
						}}
						const msgElement = document.getElementById('msg');
						msgElement.style.color = isWarning ? "#e67e22" : "#dc3545";
						msgElement.innerText = errorMessage;
      
						console.error("Firebase Error Code: ", error.code);
						console.error("Firebase Error Message:", error.message);
     				}});
         		}});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

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
			"email": email,
			"role": "user",
			"created_at": firestore.SERVER_TIMESTAMP
		})
		return {"message": "Initialize user doc successfully", "uid": uid}

	return {"message": "Synchonize successfully!", "uid": uid}

@app.post("/api/auth/me")
def get_user_profile(user_data: dict = Depends(get_current_user)):
	"""
	Get user information while signing in
	"""

	db = get_db()
	uid = user_data.get("uid")
	user_doc = db.collection("user").document(uid).get()

	if user_doc.exists:
		return user_doc.to_dict()

	return {"uid": uid, "email": user_data.get("email"), "message": "Profile has not been initialized"}

@app.get("/api/chat/sessions")
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

@app.post("/api/chat")
def chat(request: ChatRequest, user_data: dict = Depends(get_current_user)):
    uid = user_data.get("uid")
    
    save_message(request.session_id, "user", request.message, uid=uid)

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
