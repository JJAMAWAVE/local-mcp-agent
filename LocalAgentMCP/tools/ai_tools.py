import requests
from ollama_client import OllamaClient

# 기본 모델
DEFAULT_MODEL = "qwen3-coder:30b"

def ai_list_models_handler(args: dict):
    """
    로컬 Ollama에 설치된 모델 목록을 가져옵니다.
    """
    try:
        # Ollama API를 통해 태그 목록 조회
        resp = requests.get("http://localhost:11434/api/tags")
        if resp.status_code == 200:
            data = resp.json()
            models = [m["name"] for m in data.get("models", [])]
            return {"models": models}
        return {"error": "Ollama API connection failed"}
    except Exception as e:
        return {"error": str(e)}

def ai_generate(args: dict):
    prompt = args.get("prompt", "")
    model_name = args.get("model", DEFAULT_MODEL)
    schema = args.get("schema")

    client = OllamaClient(model=model_name)

    try:
        if schema:
            result = client.ask_for_json_string(prompt, schema)
        else:
            result = client.generate(prompt)

        if isinstance(result, dict):
            result.pop("context", None)
            result["_used_model"] = model_name
            return result
        
        return {"response": result, "_used_model": model_name}

    except Exception as e:
        return {"error": str(e)}

TOOL_DEFINITIONS = {
    "ai.generate": {
        "description": "Generate text using local AI",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string"},
                "model": {"type": "string"},
                "schema": {"type": "string"}
            },
            "required": ["prompt"]
        },
        "handler": ai_generate
    },
    # [추가됨] 모델 목록 조회 툴
    "ai.list_models": {
        "description": "List installed Ollama models",
        "inputSchema": {"type": "object", "properties": {}},
        "handler": ai_list_models_handler
    }
}