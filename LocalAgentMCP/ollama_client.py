# ollama_client.py
# ---------------------------------------------------------
# Qwen3-coder:30b 전용 LLM 인터페이스
# JSON-only 응답 강제 / Markdown 제거 / 중첩 JSON 처리 강화
# ---------------------------------------------------------

import json
import re
import requests
import time


class OllamaClient:
    def __init__(self, model="qwen3-coder:30b", host="http://localhost:11434"):
        self.model = model
        self.host = host.rstrip("/")

    # ---------------------------------------------------------
    # 올라마 호출 (스트리밍 X, 완전 응답)
    # ---------------------------------------------------------
    def generate(self, prompt: str, max_retries=3):
        url = f"{self.host}/api/generate"

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url,
                    json={"model": self.model, "prompt": prompt, "stream": False},
                    timeout=180
                )

                if response.status_code != 200:
                    raise RuntimeError(
                        f"Ollama HTTP Error {response.status_code}: {response.text}"
                    )

                return response.json()

            except Exception as e:
                print(f"[OllamaClient] Error: {e} (attempt {attempt+1}/{max_retries})")
                time.sleep(1)

        raise RuntimeError("Ollama generate() failed after retries")

    # ---------------------------------------------------------
    # LLM 출력에서 JSON만 추출
    # 중첩 JSON 가능 / Markdown 차단
    # ---------------------------------------------------------
    def extract_json(self, text: str):
        if not text:
            raise ValueError("No text to extract JSON from")

        # 1. Markdown 제거
        text = re.sub(r"```[a-zA-Z0-9]*", "", text)
        text = text.replace("```", "").strip()

        # 2. 전체에서 JSON 파싱을 시도
        try:
            return json.loads(text)
        except:
            pass

        # 3. 중첩 JSON 추출 (스택 기반)
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
                        candidate = text[start:i + 1]
                        try:
                            return json.loads(candidate)
                        except:
                            pass

        raise ValueError("No valid JSON found in LLM output")

    # ---------------------------------------------------------
    # JSON 스키마 강제 요청 (JSON만 반환)
    # ---------------------------------------------------------
    def ask_json(self, prompt: str, json_schema: str):
        full_prompt = f"""
You MUST output JSON with this exact schema:

{json_schema}

Rules:
- Output ONLY JSON
- NO markdown
- NO explanation
- NO extra text
- Field names must match exactly
- If value is missing, fill with empty string

User Request:
{prompt}
"""

        response = self.generate(full_prompt)
        raw = response.get("response", "")

        return self.extract_json(raw)

    # ---------------------------------------------------------
    # JSON 문자열을 강제로 받는 버전
    # ---------------------------------------------------------
    def ask_for_json_string(self, prompt: str, schema: str) -> str:
        full_prompt = f"""
Return ONLY JSON (stringified). 
NO explanation. NO markdown.

Schema:
{schema}

User Command:
{prompt}
"""

        response = self.generate(full_prompt)
        return response.get("response", "").strip()


# ---------------------------------------------------------
# 단독 실행 테스트
# ---------------------------------------------------------
if __name__ == "__main__":
    ollama = OllamaClient(model="qwen3-coder:30b")

    schema = """
{
  "command": "create_script",
  "script_name": "Test",
  "path": "Assets/Scripts",
  "content": "C# code here"
}
"""

    result = ollama.ask_json("Unity에 Player.cs 만들어줘", schema)
    print(result)
