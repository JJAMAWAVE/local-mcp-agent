import logging

logger = logging.getLogger("ComfyUIProvider")

class ComfyUIProvider:
    def __init__(self, host="http://127.0.0.1:8188"):
        self.host = host

    def generate_image(self, prompt: str, workflow: str = "default"):
        return "Image generation not implemented yet in this basic provider."
