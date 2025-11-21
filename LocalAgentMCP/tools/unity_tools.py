# unity_tools.py
from ai_pipe_client import UnityPipeClient
import json

TOOL_NAME = "unity_send"
TOOL_DESCRIPTION = "Send JSON command to Unity Editor through NamedPipe"
TOOL_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "command": {"type": "string"},
        "script_name": {"type": "string"},
        "path": {"type": "string"},
        "content": {"type": "string"}
    },
    "required": ["command"]
}

def execute(params: dict):
    try:
        result = UnityPipeClient.send(params)
        return result
    except Exception as e:
        return {"error": str(e)}
