import streamlit as st
import requests

import uuid

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
                st.session_state.session_id = str(uuid.uuid4())

                sync_url = SERVER_URL.replace("/chat", "/auth/login")
                headers = {"Authorization": f"Bearer {st.session_state.id_token}"}

                with st.spinner("Synchronize user profile..."):
                    try:
                        response = requests.post(sync_url, headers=headers)

                    except Exception as e:
                        st.error(f"Failed to synchronize: {str(e)}")
                        st.stop

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

if "user_profile" not in st.session_state:
    me_url = SERVER_URL.replace("/chat", "/auth/me")
    headers = {"Authorization": f"Bearer {st.session_state.id_token}"}
    try:
        res = requests.post(me_url, headers=headers)
        if res.status_code == 200:            
            st.session_state.user_profile = res.json()
            
            
        else:
            st.session_state.user_profile = {"email": "N/A", "role": "N/A"}
            
    except Exception as e:
        st.session_state.user_profile = {"email": "error", "role": "error"}
        st.error(f"Error while load user profile: {str(e)}")
		
user_email = st.session_state.user_profile.get("email") or "NONE"
user_role = st.session_state.user_profile.get("role") or "user"

st.sidebar.markdown(f"### 👤 {user_email}")
st.sidebar.caption(f"Role: {user_role.upper()} | ID: {st.session_state.uid[:8]}...")

def start_new_chat():
	st.session_state.session_id = str(uuid.uuid4())
	st.session_state.messages = []

def switch_chat(selected_session_id):
	st.session_state.session_id = selected_session_id
	
	if "messages" in st.session_state:
		del st.session_state["messages"]	
	

st.sidebar.divider()
st.sidebar.write("History")
st.sidebar.button("➕ Create new chat", on_click=start_new_chat, use_container_width=True)

# Call API get User session_id list
sessions_url = SERVER_URL.replace("/chat", "/chat/sessions")
headers = {"Authorization": f"Bearer {st.session_state.id_token}"}

try:
	res = requests.get(sessions_url, headers=headers)
	if res.status_code == 200:
		sessions = res.json().get("sessions", [])

		for s_id in sessions:
			short_id = s_id[:8]

			btn_type = "primary" if s_id == st.session_state.session_id else "secondary"

			st.sidebar.button(
				f"💬 Chat {short_id}...",
				key=f"btn_{s_id}",	# unique
				on_click=switch_chat,
				args=(s_id,),
				use_container_width=True,
				type=btn_type
			)

except Exception as e:
	st.sidebar.error("Failed to load chat history")

st.sidebar.divider()
st.sidebar.button("Log Out", on_click=lambda: st.session_state.clear())

st.set_page_config(page_title="AI Chatbot", page_icon="🤖")
st.title("🤖 Chatbot AI")

if "session_id" not in st.session_state: 
	st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
	st.session_state.messages = []

	try:
		url = f"{SERVER_URL}/history/{st.session_state.session_id}?limit=50"

		headers = {"Authorization": f"Bearer {st.session_state.id_token}"}

		response = requests.get(url, headers=headers)

		if response.status_code == 200:
			db_history = response.json().get("history", [])
			st.session_state.messages = db_history

		else:
			st.error(f"Backend Error: {response.text}")

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

			headers = {"Authorization": f"Bearer {st.session_state.id_token}"}

			response = requests.post(SERVER_URL, json=payload, headers=headers)

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

