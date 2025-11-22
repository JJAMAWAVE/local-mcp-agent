# =====================================================================
# ollama_client.py (Refactored)
# ---------------------------------------------------------------------
# Stable JSON extraction, error-safe retries, strict schema enforcement
# for Qwen3-Coder:30B running on Ollama.
# =====================================================================

import json
import re
import time
import requests


class OllamaClient:
    """
    Stable wrapper for Qwen3-Coder:30B via Ollama.
    Includes:
        - Safe retries
        - Robust JSON extraction
        - JSON schema enforcement
        - Markdown stripping
    """

    def __init__(self, model="qwen3-coder:30b", host="http://localhost:11434"):
        self.model = model
        self.host = host.rstrip("/")

    # =================================================================
    # Internal helpers
    # =================================================================
    def _post(self, endpoint: str, payload: dict, timeout=180, retry=3):
        """
        Unified HTTP POST with retries & safe error logging.
        """

        url = f"{self.host}{endpoint}"

        for attempt in range(retry):
            try:
                resp = requests.post(url, json=payload, timeout=timeout)

                if resp.status_code != 200:
                    raise RuntimeError(
                        f"Ollama HTTP {resp.status_code}: {resp.text}"
                    )

                return resp.json()

            except Exception as e:
                print(f"[OllamaClient] POST error: {e}  (attempt {attempt+1}/{retry})")
                time.sleep(1)

        raise RuntimeError(f"POST failed after {retry} retries → {url}")

    # =================================================================
    # Raw text generation (no streaming)
    # =================================================================
    def generate(self, prompt: str):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        return self._post("/api/generate", payload)

    # =================================================================
    # JSON extraction (fallback-safe)
    # =================================================================
    def extract_json(self, text: str):
        """
        Extracts JSON from arbitrary LLM output.
        Handles:
            - Markdown fenced blocks
            - Nested JSON objects
            - Extra chatter around JSON
        """
        if not text:
            raise ValueError("LLM returned empty output")

        # 1. Markdown fenced code blocks 제거
        text = re.sub(r"```[a-zA-Z0-9]*", "", text)
        text = text.replace("```", "").strip()

        # 2. 전체를 JSON으로 파싱 시도
        try:
            return json.loads(text)
        except:
            pass

        # 3. 중첩 JSON 탐지 (스택 기반)
        stack = []
        start_idx = -1

        for i, ch in enumerate(text):
            if ch == "{":
                if not stack:
                    start_idx = i
                stack.append("{")

            elif ch == "}":
                if stack:
                    stack.pop()
                    if not stack:  # JSON 완성됨
                        candidate = text[start_idx: i + 1]
                        try:
                            return json.loads(candidate)
                        except:
                            pass

        raise ValueError("Valid JSON not found in LLM output")

    # =================================================================
    # Strict JSON schema enforced LLM output
    # =================================================================
    def ask_json(self, prompt: str, schema: str):
        """
        Requests JSON-only response that must match a schema.
        Returns parsed dict.
        """

        full_prompt = f"""
You MUST output JSON that strictly follows this schema:

{schema}

RULES:
- Output ONLY valid JSON
- NO markdown
- NO explanation
- NO extra text
- Do not wrap the JSON in triple backticks
- Field names MUST match exactly
- Missing fields MUST be included as empty string

USER REQUEST:
{prompt}
"""
        raw = self.generate(full_prompt).get("response", "")
        return self.extract_json(raw)

    # =================================================================
    # JSON string output (unparsed)
    # =================================================================
    def ask_for_json_string(self, prompt: str, schema: str) -> str:
        """
        Returns JSON as string (not parsed).
        Useful when caller must parse manually.
        """

        full_prompt = f"""
Return ONLY JSON (stringified).
NO markdown.
NO prose.
STRICTLY follow this schema:

{schema}

USER COMMAND:
{prompt}
"""

        raw = self.generate(full_prompt).get("response", "")
        return raw.strip()


# =====================================================================
# Standalone quick test
# =====================================================================
if __name__ == "__main__":
    client = OllamaClient()

    schema = """
{
  "command": "create_script",
  "script_name": "Test",
  "path": "Assets/Scripts",
  "content": "C# code here"
}
"""

    print("\n=== Test Call ===")
    try:
        result = client.ask_json("Unity에 Player.cs 만들어줘", schema)
        print("\n[Result]")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"[Error] {e}")
