import requests
import json

UNITY_SERVER_URL = "http://127.0.0.1:8080"

def send_to_unity(payload: dict):
    try:
        # 유니티 C# 서버로 HTTP POST 전송
        resp = requests.post(UNITY_SERVER_URL, json=payload, timeout=1)
        return {"status": "executed", "unity_response": "Connected"}
    except:
        return {"status": "failed", "message": "Unity Editor Not Connected (Check Port 8080)"}

def unity_create_object_handler(args: dict):
    return send_to_unity({"command": "create_object", "args": args})

def unity_run_command_handler(args: dict):
    return send_to_unity({"command": "run", "args": args})

TOOL_DEFINITIONS = {
    "unity.create_object": {
        "description": "Spawn Object in Unity",
        "inputSchema": { "type": "object", "properties": { "object_type": {"type": "string"} }, "required": ["object_type"] },
        "handler": unity_create_object_handler
    },
    "unity.run": {
        "description": "Run Unity Command",
        "inputSchema": { "type": "object", "properties": { "command": {"type": "string"} }, "required": ["command"] },
        "handler": unity_run_command_handler
    }
}