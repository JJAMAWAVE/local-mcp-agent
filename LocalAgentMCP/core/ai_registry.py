# core/ai_registry.py
# Local AI Unified Registry (LLM / Vision / Image)

import os
import json
import requests
import base64
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# Load ai_registry.json
# ----------------------------------------------------------------------

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "..", "ai_registry.json")


def load_registry() -> Dict[str, Any]:
    if not os.path.exists(REGISTRY_PATH):
        logger.error(f"ai_registry.json not found: {REGISTRY_PATH}")
        return {}

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


aiconfig = load_registry()

# ----------------------------------------------------------------------
# Helper: HTTP wrapper
# ----------------------------------------------------------------------
def http_post(url: str, data: Dict[str, Any], headers: Dict[str, str] = {}):
    try:
        r = requests.post(url, json=data, headers=headers, timeout=300)
        return r.json()
    except Exception as e:
        logger.error(f"HTTP POST failed: {url} : {e}")
        raise e


# ----------------------------------------------------------------------
# LLM CHAT (Ollama / LMStudio)
# ----------------------------------------------------------------------
def call_llm(prompt: str, system: str = "", model_key: str = "primary"):
    """
    Unified LLM call API (Patched for Ollama streaming)
    """
    llm_cfg = aiconfig.get("llm", {})
    if not llm_cfg:
        raise Exception("LLM config missing in ai_registry.json")

    target = llm_cfg.get(model_key)
    if not target:
        raise Exception(f"LLM model key not found: {model_key}")

    provider = target.get("provider")
    url = target.get("url")
    model = target.get("model")

    logger.info(f"LLM Call → provider={provider} model={model}")

    # --------------------------------------------------
    # Ollama (Streaming-safe)
    # --------------------------------------------------
    if provider == "ollama":
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True
        }

        try:
            with requests.post(f"{url}/api/generate", json=payload, stream=True, timeout=300) as r:
                r.raise_for_status()

                full_text = []

                for line in r.iter_lines():
                    if not line:
                        continue
                    try:
                        obj = json.loads(line.decode("utf-8"))
                        chunk = obj.get("response", "")
                        if chunk:
                            full_text.append(chunk)
                    except:
                        continue

                return "".join(full_text)

        except Exception as e:
            logger.error(f"Ollama LLM Error: {e}")
            return f"[ERROR] Ollama call failed: {e}"

    # --------------------------------------------------
    # LM Studio (OpenAI-like)
    # --------------------------------------------------
    if provider == "lmstudio":
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ]
        }
        result = http_post(f"{url}/chat/completions", payload)
        return result["choices"][0]["message"]["content"]

    raise Exception(f"Unsupported LLM provider: {provider}")


# ----------------------------------------------------------------------
# VISION ANALYZE
# ----------------------------------------------------------------------
def call_vision(image_path: str, prompt: str):
    vision_cfg = aiconfig.get("vision", {})
    if not vision_cfg:
        raise Exception("vision config missing in ai_registry.json")

    provider = vision_cfg.get("provider")
    url = vision_cfg.get("url")
    model = vision_cfg.get("model")

    logger.info(f"Vision Analyze → provider={provider} model={model}")

    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    if provider == "lmstudio":
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt},
                {
                    "role": "user",
                    "content": {
                        "type": "image_url",
                        "image_url": f"data:image/png;base64,{img_b64}"
                    }
                }
            ]
        }
        result = http_post(f"{url}/chat/completions", payload)
        return result["choices"][0]["message"]["content"]

    raise Exception(f"Unsupported vision provider: {provider}")


# ----------------------------------------------------------------------
# IMAGE GENERATION (Stable Diffusion via ComfyUI)
# ----------------------------------------------------------------------
def generate_image(prompt: str, workflow: str = None):
    img_cfg = aiconfig.get("image", {})
    if not img_cfg:
        raise Exception("image config missing in ai_registry.json")

    provider = img_cfg.get("provider")
    url = img_cfg.get("url")
    wf = workflow or img_cfg.get("workflow")

    logger.info(f"Image Generate → provider={provider} workflow={wf}")

    if provider == "comfyui":
        payload = {
            "prompt": prompt,
            "workflow": wf
        }
        result = http_post(f"{url}/prompt", payload)
        return result

    raise Exception(f"Unsupported image provider: {provider}")
