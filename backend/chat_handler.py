# backend/chat_handler.py

import requests

class ChatEngine:
    def __init__(self, model_name="llama3"):
        self.model_url = "http://localhost:11434/api/chat"
        self.model_name = model_name

    def query(self, messages):
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False
        }
        try:
            res = requests.post(self.model_url, json=payload, headers=headers, timeout=60)
            res.raise_for_status()
            data = res.json()
            return data.get("message", {}).get("content", "[No response from model]").strip()
        except Exception as e:
            return f"[Error querying model: {e}]"