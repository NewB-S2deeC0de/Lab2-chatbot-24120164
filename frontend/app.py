import streamlit as st
import streamlit.components.v1 as components
import requests

import uuid

from auth import register_with_email, login_with_email

SERVER_URL = "http://localhost:8000/chat"

# 1. BARRIER: CATCH TOKEN FROM GOOGLE
if "id_token" in st.query_params and "uid" in st.query_params:
    token = st.query_params["id_token"]
    uid = st.query_params["uid"]

    sync_url = SERVER_URL.replace("/chat", "/auth/login")
    headers = {"Authorization": f"Bearer {token}"}

    try:
        res = requests.post(sync_url, headers=headers)
        if res.status_code == 200:
            st.session_state.id_token = token
            st.session_state.uid = uid
            st.session_state.session_id = str(uuid.uuid4())

            st.query_params.clear()
            st.rerun()

        else:
            st.error("Error: Failed to sync data between Google and Backend")

    except Exception as e:
        st.error(f"Backend Error: {e}")

# 2. BARRIER: LOGIN/ REGISTER FOR FIRST LOAD
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
                        st.stop()

                st.success("Login Successfully!")
                st.rerun()

            else:
                st.error(f"Error: {res.get('error', {}).get('message', 'Wrong Information')}")
            
            pass
        
        st.divider()
        st.markdown("<p style='text-align: center; color: gray;'>OR</p>", unsafe_allow_html=True)
        
        # Draw Google Button
        google_btn_html = """
        <a href="http://localhost:8000/auth/google/ui" target="_self" style="
            text-decoration: none; width: 100%; padding: 8px 16px;
            background-color: white; color: #3c4043;
            border: 1px solid #dadce0; border-radius: 4px;
            font-family: Roboto, Arial, sans-serif; font-size: 14px; font-weight: 500;
            display: flex; align-items: center; justify-content: center;
            gap: 10px; box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3);
            box-sizing: border-box;
        ">
            <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" style="width: 18px; height: 18px;">
            Continue with Google
        </a>
        """
        st.markdown(google_btn_html, unsafe_allow_html=True)
        
    
    with tab2:
        email_reg = st.text_input("Email", key="reg_email")
        pass_reg = st.text_input("Password (At least six characters)", type="password", key="reg_pass")
        if st.button("Register", type="primary"):
            res = register_with_email(email_reg, pass_reg)
            if "idToken" in res:
                st.success("Register successfully! Please move to Login.")
            else:
                st.error(f"Error: {res.get('error', {}).get('message', 'Request was denied')}")
             
        st.stop()
# ====================================================================
# FOR USER LOGIN SUCCESSFULLY
# ====================================================================

#  3.  FETCH USER PROFILE
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
        


# 5. SIDEBAR DISPLAY
st.markdown("""
            <style>
            .user-avatar {
                display: block; 
                margin-left: auto;
                margin-right: auto;
                border-radius: 50%;
                border: 2px solid #4285F4;
                object-fit: cover;
            }
            .user-info {
                text-align: center;
                padding-top: 10px;
            }
            </style>
""", unsafe_allow_html=True)
with st.sidebar:
    profile = st.session_state.get("user_profile", {})
    user_username = profile.get("username", "Guest")
    user_email = profile.get("email") or "NONE"
    user_role = profile.get("role") or "user"
    user_avatar = profile.get("avatar_url") or "https://www.w3schools.com/howto/img_avatar.png"
    
    st.markdown(f'<img src="{user_avatar}" class="user-avatar" width="80">', unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="user-info">
            <h3 style="margin-bottom: 0;">{user_username}</h3>
            <p style="color: gray; font-size: 0.9em;">{user_email}</p>
        </div>
        """, unsafe_allow_html=True)
    
    role_color = "#FF4B4B" if user_role.lower() == "admin" else "#00C781"
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <span style="background-color: {role_color}; color: white; padding: 2px 10px; border-radius: 10px; font-size: 0.8em; font-weight: bold;">
                {user_role.upper()}
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Function for user chat multi-session
    def start_new_chat():
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
    
    def switch_chat(selected_session_id):
        st.session_state.session_id = selected_session_id
        
        if "messages" in st.session_state:
            del st.session_state["messages"]
            
    st.write("📂 **History**")
    st.button("➕ Create new chat", on_click=start_new_chat, use_container_width=True)
            
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
        st.sidebar.error("Load Error: Failed")
        
    st.divider()
    if st.button("🚪Log Out", use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.set_page_config(page_title="AI Chatbot", page_icon="🤖")
st.title("🤖 Chatbot AI")

# 6. LOAD CHAT HISTORY
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
        st.error(f"Load Error: {str(e)}")

# Reder chat history per web reload 
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 7. CALL MODEL TO GENERATE ANSWER
# Chat input box
if prompt := st.chat_input("Ask me something..."):
    # Render chat history
    with st.chat_message("user"):
        st.markdown(prompt)

    # Save into streamlit state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Send request to Backend API
    with st.spinner("Braining..."):
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
                bot_reply = f"Error Backend {response.text}"

        except Exception as e:
            bot_reply = f"Connection Error: Can not call FastAPI {e}"

    # Render bot_reply
        with st.chat_message("assistant"):
            st.markdown(bot_reply)

    # Save into state
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

