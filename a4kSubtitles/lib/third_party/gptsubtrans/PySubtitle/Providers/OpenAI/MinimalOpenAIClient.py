import requests
import logging

class MinimalOpenAIClient:
    def __init__(self, api_key, api_base=None, timeout=60):
        self.api_key = api_key
        self.api_base = api_base or "https://api.openai.com/v1"
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def chat_completion(self, model, messages, temperature=0.0, **kwargs):
        url = f"{self.api_base}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        try:
            resp = self.session.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logging.error(f"OpenAI API request failed: {e}")
            raise

    def instruct_completion(self, model, prompt, temperature=0.0, max_tokens=2048, **kwargs):
        url = f"{self.api_base}/completions"
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        try:
            resp = self.session.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logging.error(f"OpenAI API request failed: {e}")
            raise

    def list_models(self):
        url = f"{self.api_base}/models"
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logging.error(f"OpenAI API request failed: {e}")
            raise
