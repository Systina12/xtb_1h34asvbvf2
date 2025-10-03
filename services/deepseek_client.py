import requests
from config.settings import DEEPSEEK_API_URL, DEEPSEEK_MODEL

class DeepSeekClient:
    def __init__(self, api_key: str, timeout: int = 30):
        self.api_key = api_key
        self.timeout = timeout

    def chat(self, prompt: str) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        data = {
            "model": DEEPSEEK_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "stream": False
        }
        resp = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()
        js = resp.json()
        return js['choices'][0]['message']['content'].strip()