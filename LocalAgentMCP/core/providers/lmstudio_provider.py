import logging

logger = logging.getLogger("LMStudioProvider")

class LMStudioProvider:
    def __init__(self, host="http://localhost:1234"):
        self.host = host

    def generate_text(self, prompt: str, system: str = "", model: str = "local-model"):
        return "LMStudio generation not implemented yet."
