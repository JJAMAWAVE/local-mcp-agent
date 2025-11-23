import sys
import os

# core 모듈을 찾기 위해 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__)))

from core.ai_registry import AIRegistry, config

print("=== Character Config Test ===")
for name, data in config.get("characters", {}).items():
    print(f"\n[Character: {name}]")
    print(f"Role: {data.get('role')}")
    print(f"Model: {data.get('model')}")
    print(f"System Prompt Length: {len(data.get('system_prompt', ''))}")
    print("-" * 30)

print("\n=== Mock Call Test ===")
# 실제 LLM 호출은 비용/시간 문제로 생략하고, 설정 로드만 확인
# 만약 실제 호출을 원하면 아래 주석 해제
# print(AIRegistry.call_llm("안녕, 너는 누구니?", character_name="mia"))
