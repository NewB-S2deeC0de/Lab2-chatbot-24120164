import streamlit as st

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from backend.dependencies.auth import get_current_user
from backend.core.firebase_config import get_db
from firebase_admin import firestore

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
def sync_user(user_data: dict = Depends(get_current_user)):
	"""
	Synchronize User from Firebase Auth to Firestore
	"""

	db = get_db()
	uid = user_data.get("uid")
	email = user_data.get("email")
 
	username = user_data.get("name",  email.split('@')[0])
	avatar_url = user_data.get("picture", "")
	provider = user_data.get("firebase", {}).get("sign_in_provider", "email")
 
	user_ref = db.collection("user").document(uid)
	user_doc = user_ref.get()

	user_info = {
		"email": email, 
		"username": username,
		"avatar_url": avatar_url, 
		"provider": provider, 
		"last_login_at": firestore.SERVER_TIMESTAMP,
		"role": "user"
	}
	if not user_doc.exists:
		user_info["created_at"] = firestore.SERVER_TIMESTAMP
		user_ref.set(user_info)
	else:
		user_ref.update({
			"username": username,
			"avatar_url": avatar_url,
			"last_login_at": firestore.SERVER_TIMESTAMP
		})

	return {"message": "Synchonize successfully!", "uid": uid}

@router.post("/me")
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

API_KEY = st.secrets["apiKey"]
AUTH_DOMAIN = st.secrets["authDomain"]
PROJECT_ID = st.secrets["projectId"]
STORAGE_BUCKET = st.secrets["storageBucket"]
MESSAGING_SENDER_ID = st.secrets["messagingSenderId"]
APP_ID = st.secrets["appId"]

@router.get("/google/ui", response_class=HTMLResponse)
def google_login_ui():
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Google Validation</title>
        <meta charset="utf-8">
        <link rel="icon" href="/favicon.ico" type="image/x-icon">
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