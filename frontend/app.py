import streamlit as st
import requests
from auth import register_with_email, login_with_email

SERVER_URL = "http://localhost:8000/api/chat"

if "id_token" not in st.session_state:
    st.title("Login to AI Chatbot")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        email_login = st.text_input("Email", key="login_email")
        pass_login = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", type="primary"):
            res = login_with_email(email_login, pass_login)
            if "idToken" in res:
                st.session_state.id_token = res["idToken"]
                st.session_state.uid = res["localId"]
                st.session_state.session_id = res["localId"]
                st.success("Login Successfully!")
                st.rerun()
                
            else:
                st.error(f"Error: {res.get('error', {}).get('message', 'Wrong Information')}")
    with tab2:
        email_reg = st.text_input("Email", key="reg_email")
        pass_reg = st.text_input("Email (At least six charaters)", type="password", key="reg_pass")
        if st.button("Register", type="primary"):
            res = register_with_email(email_reg, pass_reg)
            if "idToken" in res:
                st.success("Register successfully! Please move to Login.")
            else:
            	st.error(f"Error: {res.get('error', {}).get('message', 'Request was denied')}")
    
    st.stop()
        
st.sidebar.write(f"Login with ID: {st.session_state.uid}")
st.sidebar.button("Log Out", on_click=lambda: st.session_state.clear())
 

st.set_page_config(page_title="AI Chatbot", page_icon="🤖")
st.title("🤖 Chatbot AI")

if "session_id" not in st.session_state: 
	st.session_state.session_id = "test_user_streamlit_01"

if "messages" not in st.session_state:
	st.session_state.messages = []

	try:
		url = f"{SERVER_URL}/history/{st.session_state.session_id}?limit=50"
		response = requests.get(url)

		if response.status_code == 200:
			db_history = response.json().get("history", [])
			st.session_state.messages = db_history

	except Exception as e:
		st.error(f"Lỗi khi tải lịch sử: {str(e)}")

# Reder chat history per web reload 
for msg in st.session_state.messages:
	with st.chat_message(msg["role"]):
		st.markdown(msg["content"])

# Chat input box
if prompt := st.chat_input("Chia sẻ vấn đề của bạn ở đây"):
	# Render chat history
	with st.chat_message("user"):
		st.markdown(prompt)

	# Save into streamlit state
	st.session_state.messages.append({"role": "user", "content": prompt})

	# Send request to Backend API
	with st.spinner("AI đang đặt mình vào vị trí của bạn..."):
		try: 
			payload = {
				"session_id": st.session_state.session_id, 
				"message": prompt
			}

			response = requests.post(SERVER_URL, json=payload)

			if response.status_code == 200:
				bot_reply = response.json().get("bot_reply")
			else:
				bot_reply = f"Lỗi Backend {response.text}"

		except Exception as e:
			bot_reply = f"Lỗi kết nối: Không thể gọi tới FastAPI {e}"

	# Render bot_reply
		with st.chat_message("assistant"):
			st.markdown(bot_reply)

	# Save into state
		st.session_state.messages.append({"role": "assistant", "content": bot_reply})

