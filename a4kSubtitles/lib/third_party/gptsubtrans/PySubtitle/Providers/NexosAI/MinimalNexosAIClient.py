import requests
import logging


class MinimalNexosAIClient:
    """
    Minimal Nexos AI Client for interacting with Nexos AI API endpoints.
    Supports chat, completions, embeddings, audio, and model listing.
    """
    def __init__(self, api_key, api_base=None, timeout=60):
        self.api_key = api_key
        self.api_base = api_base or "https://api.nexos.ai/v1"
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def chat_completion(self, model, messages, temperature=0.0, max_completion_tokens=None, **kwargs):
        import json
        """
        Call the Nexos AI chat completion endpoint.
        Args:
            model (str): Model ID.
            messages (list): List of message dicts.
            temperature (float): Sampling temperature.
            max_completion_tokens (int, optional): Max tokens for completion.
            **kwargs: Additional parameters.
        Returns:
            dict: API response.
        """
        url = f"{self.api_base}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_completion_tokens is not None:
            payload["max_completion_tokens"] = max_completion_tokens
        payload.update(kwargs)
        try:
            resp = self.session.post(url, json=payload, timeout=self.timeout)
            if resp.status_code >= 400:
                logging.error(f"Nexos AI API error response: {resp.text}")
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logging.error(f"Nexos AI API request failed: {e}")
            raise

    def instruct_completion(self, model, prompt, temperature=0.0, max_tokens=2048, **kwargs):
        """
        Call the Nexos AI completions endpoint (deprecated in favor of chat).
        Args:
            model (str): Model ID.
            prompt (str): Prompt string.
            temperature (float): Sampling temperature.
            max_tokens (int): Max tokens for completion.
            **kwargs: Additional parameters.
        Returns:
            dict: API response.
        """
        url = f"{self.api_base}/completions"
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        payload.update(kwargs)
        try:
            resp = self.session.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logging.error(f"Nexos AI API request failed: {e}")
            raise

    def embeddings(self, model, input, encoding_format="float", dimensions=None, **kwargs):
        """
        Call the Nexos AI embeddings endpoint.
        Args:
            model (str): Model ID.
            input (str or list): Input text(s).
            encoding_format (str): 'float' or 'base64'.
            dimensions (int, optional): Number of dimensions.
            **kwargs: Additional parameters.
        Returns:
            dict: API response.
        """
        url = f"{self.api_base}/embeddings"
        payload = {
            "model": model,
            "input": input,
            "encoding_format": encoding_format,
        }
        if dimensions is not None:
            payload["dimensions"] = dimensions
        payload.update(kwargs)
        try:
            resp = self.session.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logging.error(f"Nexos AI API request failed: {e}")
            raise

    def audio_speech(self, model, input, voice, response_format="mp3", speed=1, **kwargs):
        """
        Call the Nexos AI audio speech endpoint.
        Args:
            model (str): Model ID.
            input (str): Text to generate audio for.
            voice (str): Voice to use.
            response_format (str): Output format (mp3, wav, etc).
            speed (float): Speed of generated audio.
            **kwargs: Additional parameters.
        Returns:
            dict: API response.
        """
        url = f"{self.api_base}/audio/speech"
        payload = {
            "model": model,
            "input": input,
            "voice": voice,
            "response_format": response_format,
            "speed": speed,
        }
        payload.update(kwargs)
        try:
            resp = self.session.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logging.error(f"Nexos AI API request failed: {e}")
            raise

    def list_models(self):
        """
        List available models from Nexos AI.
        Returns:
            list: List of model names (str).
        """
        url = f"{self.api_base}/models"
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            # Nexos API may return {"data": [{"id": ...}, ...]} or similar
            if isinstance(data, dict):
                if "data" in data and isinstance(data["data"], list):
                    return [{"id": m["id"], "name": m['name'], "provider": m["owned_by"]} for m in data["data"] if "id" in m and "name" in m and "owned_by" in m]
                # fallback: if data itself is a list of models
                elif isinstance(data.get("models"), list):
                    return [{"id": m["id"], "name": m['name'], "provider": m["owned_by"]} for m in data["models"] if "id" in m and "name" in m and "owned_by" in m]
            elif isinstance(data, list):
                return [{"id": m["id"], "name": m['name'], "provider": m["owned_by"]} for m in data if "id" in m and "name" in m and "owned_by" in m]
            return []
        except requests.RequestException as e:
            logging.error(f"Nexos AI API request failed: {e}")
            return []
