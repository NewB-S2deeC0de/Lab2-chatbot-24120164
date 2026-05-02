import requests

OLLAMA_URL = "http://localhost:11434/api/chat"

def get_ai_result(user_message: str) -> str: 
	payload = {
		"model": "llama3.2:1b",
		"messages": [{"role": "user", "content": user_message}], 
		"stream": False
	}

	response = requests.post(OLLAMA_URL, json=payload)
	if response.status_code == 200:
		return response.json()["message"]["content"]
	else:
		raise Exception(f"Ollama error: {response.text}")
