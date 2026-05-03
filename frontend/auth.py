import requests
import streamlit as st

API_KEY = st.secrets["apiKey"]

def register_with_email(email: str, password: str):
	"""Send sign up request to Firebase"""
	url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
	payload = {"email": email, "password": password, "returnSecureToken": True}
	response = requests.post(url, json=payload)
	return response.json()

def login_with_email(email: str, password: str):
	"""Send sign in request to Firebase"""
	url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
	payload = {"email": email, "password": password, "returnSecureToken": True}
	response = requests.post(url, json=payload)
	print(f"Mã trạng thái HTTP: {response.status_code}")
	print(f"Google trả về chính xác là: {response.text}")
	return response.json()
