import streamlit as st
import requests

SERVER_URL = "http://localhost:8000/api/chat"

st.set_page_config(page_title="AI Chatbot", page_icon="🤖")
st.title("🤖 Chatbot AI")

if "session_id" not in st.session_state: 
	st.session_state.session_id = "test_user_streamlit_01"

if "messages" not in st.session_state:
	st.session_state.messages = []

	try:
		url = f"{SERVER_URL}/history/{st.session_state.session_id}"
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

