import requests
import json
import logging

logger = logging.getLogger("OllamaProvider")

class OllamaProvider:
    def __init__(self, host="http://localhost:11434"):
        self.host = host

    def generate_text(self, prompt: str, system: str = "", model: str = "qwen2.5-coder:14b"):
        url = f"{self.host}/api/generate"
        
        full_prompt = prompt
        if system:
            full_prompt = f"System: {system}\nUser: {prompt}"

        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return f"Error: {e}"

    def analyze_image(self, image_path: str, prompt: str, model: str = "llava"):
        # Placeholder for vision
        return "Vision not implemented yet in this basic provider."
