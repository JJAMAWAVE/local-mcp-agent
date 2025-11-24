#!/usr/bin/env python3
"""studio_server.py에 텍스트 기반 도구 호출 파싱 추가"""

# 파일 읽기
with open("LocalAgentMCP/studio_server.py", "r", encoding="utf-8") as f:
    content = f.read()

# 도구 호출 파싱 함수 추가
parse_tool_function = '''
def parse_text_tool_call(content: str):
    """텍스트로 반환된 도구 호출 파싱 (qwen2.5-coder 등)"""
    import re
    try:
        # JSON 형식 찾기
        json_match = re.search(r'\\{[^{}]*"name"[^{}]*"arguments"[^{}]*\\}', content, re.DOTALL)
        if json_match:
            tool_json = json.loads(json_match.group())
            return {
                "tool_calls": [{
                    "function": {
                        "name": tool_json.get("name"),
                        "arguments": tool_json.get("arguments", {})
                    }
                }]
            }
    except:
        pass
    return None

'''

# import json 다음에 함수 추가
import_pos = content.find('import json\n') + len('import json\n')
content = content[:import_pos] + parse_tool_function + content[import_pos:]

# 도구 호출 체크 부분 수정
old_check = '''                    # 4. 툴 사용 여부 체크
                    if isinstance(ai_msg, dict) and ai_msg.get("tool_calls"):'''

new_check = '''                    # 4. 툴 사용 여부 체크
                    # 텍스트 응답에서 도구 호출 파싱 시도 (qwen2.5-coder 등)
                    if isinstance(ai_msg, dict) and not ai_msg.get("tool_calls"):
                        text_content = ai_msg.get("content", "")
                        parsed = parse_text_tool_call(text_content)
                        if parsed:
                            ai_msg = parsed
                            print(f"🔍 [Text Tool Parsed] 텍스트에서 도구 호출 감지!")
                    
                    if isinstance(ai_msg, dict) and ai_msg.get("tool_calls"):'''

content = content.replace(old_check, new_check)

# 파일 쓰기
with open("LocalAgentMCP/studio_server.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 텍스트 도구 호출 파싱 로직이 추가되었습니다!")
print("📝 qwen2.5-coder 같은 모델의 텍스트 도구 응답을 자동으로 파싱합니다.")
print("🔄 서버를 재시작하세요: Ctrl+C 후 Start_Studio.bat 실행")
