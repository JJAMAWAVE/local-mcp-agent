import os
import json
import logging
from typing import Dict, Any

from .providers.ollama_provider import OllamaProvider
from .providers.lmstudio_provider import LMStudioProvider
from .providers.comfyui_provider import ComfyUIProvider

logger = logging.getLogger(__name__)


# -------------------------------------------------------------
# Load ai_registry.json
# -------------------------------------------------------------
REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "..", "ai_registry.json")

def load_config() -> Dict[str, Any]:
    if not os.path.exists(REGISTRY_PATH):
        logger.error(f"ai_registry.json not found: {REGISTRY_PATH}")
        return {}

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


config = load_config()


# -------------------------------------------------------------
# Provider Factory
# -------------------------------------------------------------
def get_provider(provider_name: str):
    """Return provider instance by name"""
    name = provider_name.lower()

    if name == "ollama":
        return OllamaProvider()
    if name == "lmstudio":
        return LMStudioProvider()
    if name == "comfyui":
        return ComfyUIProvider()

    raise Exception(f"Unsupported provider: {provider_name}")


# -------------------------------------------------------------
# Public API — Local AI Unified Interface
# -------------------------------------------------------------
class AIRegistry:

    @staticmethod
    def call_llm(prompt: str, system: str = "", model_key: str = "primary"):
        """Unified entry point for text generation"""
        llm_cfg = config.get("llm", {})
        if model_key not in llm_cfg:
            raise Exception(f"LLM model key not found: {model_key}")

        target = llm_cfg[model_key]
        provider_name = target["provider"]
        model = target["model"]

        provider = get_provider(provider_name)
        logger.info(f"LLM Call → provider={provider_name}, model={model}")

        return provider.generate_text(prompt=prompt, system=system, model=model)


    @staticmethod
    def call_vision(image_path: str, prompt: str, model_key: str = "primary"):
        """Analyze image content"""
        vision_cfg = config.get("vision", {})
        if model_key not in vision_cfg:
            raise Exception(f"Vision model key not found: {model_key}")

        target = vision_cfg[model_key]
        provider_name = target["provider"]
        model = target["model"]

        provider = get_provider(provider_name)

        logger.info(f"Vision Call → provider={provider_name}, model={model}")

        return provider.analyze_image(image_path=image_path, prompt=prompt, model=model)


    @staticmethod
    def generate_image(prompt: str, workflow: str = None, model_key: str = "diffusion"):
        """Stable Diffusion / ComfyUI image generate"""
        image_cfg = config.get("image", {})
        if model_key not in image_cfg:
            raise Exception(f"Image model key not found: {model_key}")

        target = image_cfg[model_key]
        provider_name = target["provider"]
        default_workflow = target.get("workflow")

        provider = get_provider(provider_name)

        final_workflow = workflow or default_workflow
        logger.info(f"Image Generate → provider={provider_name}, workflow={final_workflow}")

        return provider.generate_image(prompt=prompt, workflow=final_workflow)
