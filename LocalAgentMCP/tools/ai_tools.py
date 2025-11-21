# ai_tools.py
from ollama_client import OllamaClient

TOOL_NAME = "ai_generate"
TOOL_DESCRIPTION = "Generate text using local AI model (qwen3-coder:30b by default)"
TOOL_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "prompt": {"type": "string", "description": "Prompt text"},
        "schema": {"type": "string", "description": "Optional enforced JSON schema"}
    },
    "required": ["prompt"]
}

ollama = OllamaClient(model="qwen3-coder:30b")

def execute(args: dict):
    prompt = args.get("prompt", "")
    schema = args.get("schema")

    if schema:
        return ollama.ask_for_json_string(prompt, schema)

    return ollama.generate(prompt)
