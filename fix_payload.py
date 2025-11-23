#!/usr/bin/env python3
"""studio_server.py의 payload 변수 누락 문제 수정"""
import re

# 파일 읽기
with open("LocalAgentMCP/studio_server.py", "r", encoding="utf-8") as f:
    content = f.read()

# 삽입할 payload 생성 코드
payload_code = """
            # Payload 생성
            payload = {
                "model": current_model.get("name", "qwen2.5-coder:14b"),
                "messages": [
                    {"role": "system", "content": current_model.get("system_prompt", "")}
                ] + history_storage[model_key],
                "tools": ollama_tools,
                "stream": False
            }
            """

# ollama_tools 배열 생성 후, try 문 전에 payload 코드 삽입
# 패턴: "                })\n            try:" 를 찾아서 payload_code를 중간에 삽입
pattern = r'(                \}\)\n)(            try:)'
replacement = r'\1' + payload_code + r'\2'

content = re.sub(pattern, replacement, content)

# 파일 쓰기
with open("LocalAgentMCP/studio_server.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ payload 생성 코드가 추가되었습니다!")
