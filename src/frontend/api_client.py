import requests
import os

# Default to localhost if not set
API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000/api")

def send_chat(message: str, thread_id: str):
    try:
        response = requests.post(f"{API_URL}/chat", json={"message": message, "thread_id": thread_id})
        if response.status_code == 200:
            return response.json()
        return {"error": f"Status {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

def approve_request(payload: dict, approved: bool):
    try:
        response = requests.post(f"{API_URL}/aprobar", json={"payload": payload, "approved": approved})
        if response.status_code == 200:
            return response.json()
        return {"error": f"Status {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}
