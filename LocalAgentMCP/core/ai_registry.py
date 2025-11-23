import os
import json
import logging
from typing import Dict, Any

# Provider 클래스들이 있다고 가정 (기존 구조 유지)
from .providers.ollama_provider import OllamaProvider
from .providers.lmstudio_provider import LMStudioProvider
from .providers.comfyui_provider import ComfyUIProvider

logger = logging.getLogger(__name__)

# -------------------------------------------------------------
# Load Configuration
# -------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(BASE_DIR, "ai_registry.json")
CHARACTERS_DIR = os.path.join(BASE_DIR, "characters")

def load_config() -> Dict[str, Any]:
    config = {}
    
    # 1. Load Base Registry
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        logger.error(f"ai_registry.json not found: {REGISTRY_PATH}")

    # 2. Load Character Details
    if os.path.isdir(CHARACTERS_DIR):
        for filename in os.listdir(CHARACTERS_DIR):
            if filename.endswith(".json"):
                char_name = filename[:-5] # remove .json
                try:
                    with open(os.path.join(CHARACTERS_DIR, filename), "r", encoding="utf-8") as f:
                        char_data = json.load(f)
                        
                        # Merge into config['characters']
                        if "characters" not in config:
                            config["characters"] = {}
                        
                        # Existing config (from ai_registry.json) takes precedence for connection info,
                        # but we enrich it with prompts from the character file.
                        if char_name in config["characters"]:
                            config["characters"][char_name].update(char_data)
                        else:
                            # If not in registry but file exists, add it (assuming default provider)
                            char_data["provider"] = char_data.get("provider", "ollama") # Default
                            char_data["model"] = char_data.get("base_model", "qwen2.5-coder:14b")
                            config["characters"][char_name] = char_data
                            
                except Exception as e:
                    logger.error(f"Failed to load character {filename}: {e}")

    return config

# Load once on module import
config = load_config()

# -------------------------------------------------------------
# Provider Factory
# -------------------------------------------------------------
def get_provider(provider_name: str):
    """Return provider instance by name"""
    name = provider_name.lower()
    if name == "ollama": return OllamaProvider()
    if name == "lmstudio": return LMStudioProvider()
    if name == "comfyui": return ComfyUIProvider()
    raise Exception(f"Unsupported provider: {provider_name}")

# -------------------------------------------------------------
# Public API — Local AI Unified Interface
# -------------------------------------------------------------
class AIRegistry:

    @staticmethod
    def reload():
        """Reload configuration from disk"""
        global config
        config = load_config()
        logger.info("AI Registry Reloaded")

    @staticmethod
    def call_llm(prompt: str, system: str = "", character_name: str = "mia"):
        """
        통합 텍스트 생성 (캐릭터 이름으로 호출)
        기본값: mia (코딩 담당)
        """
        # 1. 캐릭터 설정 가져오기
        char_config = config.get("characters", {}).get(character_name)
        
        # 오타나 설정 누락 시 '미아'를 기본으로
        if not char_config:
            logger.warning(f"Character '{character_name}' not found. Fallback to 'mia'.")
            char_config = config.get("characters", {}).get("mia")

        if not char_config:
            return "[System Error] ai_registry.json에 'mia' 설정이 없습니다."

        # 2. 정보 추출
        provider_name = char_config.get("provider", "ollama")
        model = char_config.get("model", char_config.get("base_model", "qwen2.5-coder:14b"))
        
        # 3. System Prompt 병합
        # 캐릭터 고유 프롬프트가 있으면 그것을 기본으로 사용
        char_system_prompt = char_config.get("system_prompt", "")
        
        final_system = char_system_prompt
        if system:
            # 호출 시 전달된 시스템 프롬프트가 있다면 추가 (또는 덮어쓰기 정책 결정)
            # 여기서는 뒤에 덧붙이는 방식으로 처리
            final_system = f"{char_system_prompt}\n\n[Additional Instructions]\n{system}"

        # 4. Provider 호출
        try:
            provider = get_provider(provider_name)
            logger.info(f"🤖 AI Call: [{character_name.upper()}] using [{model}]")
            return provider.generate_text(prompt=prompt, system=final_system, model=model)
        except Exception as e:
            return f"[Error] AI Call Failed: {e}"

    @staticmethod
    def call_vision(image_path: str, prompt: str, model_key: str = "primary"):
        vision_cfg = config.get("vision", {})
        if model_key not in vision_cfg: return "[Error] Vision config not found"
        target = vision_cfg[model_key]
        provider = get_provider(target["provider"])
        return provider.analyze_image(image_path=image_path, prompt=prompt, model=target["model"])

    @staticmethod
    def generate_image(prompt: str, workflow: str = None, model_key: str = "diffusion"):
        image_cfg = config.get("image", {})
        if model_key not in image_cfg: return "[Error] Image config not found"
        target = image_cfg[model_key]
        provider = get_provider(target["provider"])
        final_workflow = workflow or target.get("workflow")
        return provider.generate_image(prompt=prompt, workflow=final_workflow)