# ai_unity_agent.py
import json
import logging
from ai_pipe_client import UnityPipeClient
from ollama_client import OllamaClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

ollama = OllamaClient(model="qwen3-coder:30b")

UNITY_SCHEMA = """{
  "command": "create_script",
  "script_name": "MyScript",
  "path": "Assets/Scripts",
  "content": "C# code here"
}"""

def extract_json(text):
    import re
    text = re.sub(r"```[a-zA-Z0-9]*", "", text)
    text = text.replace("```", "").strip()

    try:
        return json.loads(text)
    except:
        pass

    stack = []
    start = -1
    for i, ch in enumerate(text):
        if ch == "{":
            if not stack:
                start = i
            stack.append("{")
        elif ch == "}":
            if stack:
                stack.pop()
                if not stack:
                    candidate = text[start:i+1]
                    try:
                        return json.loads(candidate)
                    except:
                        pass

    raise ValueError("No valid JSON found in LLM output")


print("=== Unity AI Agent Ready ===\n")

while True:
    try:
        command = input("명령 > ").strip()
        if not command:
            continue

        prompt = f"""
Convert natural language into Unity editor JSON command.

User: {command}

Schema:
{UNITY_SCHEMA}

Rules:
- Output ONLY JSON
- No markdown, no explanation
"""

        resp = ollama.generate(prompt)
        raw = resp.get("response", "")
        logger.info(f"LLM Output: {raw}")

        json_payload = extract_json(raw)

        logger.info(f"Sending to Unity: {json.dumps(json_payload, indent=2)}")

        unity_result = UnityPipeClient.send(json_payload)

        print(f"\n[Unity 응답] {unity_result}\n")

    except Exception as e:
        logger.error(f"Error: {e}")
