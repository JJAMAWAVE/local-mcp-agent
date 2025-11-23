import logging
import sys
import os

# Ensure core is in path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from core.ai_registry import AIRegistry

logger = logging.getLogger("AITools")

def call_llm(args):
    prompt = args.get("prompt")
    system = args.get("system", "")
    character = args.get("character", "mia")
    
    if not prompt:
        return "Error: Prompt is required"
        
    return AIRegistry.call_llm(prompt, system, character)

TOOL_DEFINITIONS = {
    "ai.call_llm": {
        "description": "Call a local LLM character (lucia, mia, nadia)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "The prompt to send"},
                "system": {"type": "string", "description": "System instruction (optional)"},
                "character": {"type": "string", "description": "Character name: lucia, mia, nadia"}
            },
            "required": ["prompt"]
        },
        "handler": call_llm
    }
}
