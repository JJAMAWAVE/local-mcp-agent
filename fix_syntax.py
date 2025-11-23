#!/usr/bin/env python3
"""studio_server.py의 SyntaxError 수정 스크립트"""

# 파일 읽기
with open("LocalAgentMCP/studio_server.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# 226번째 줄 다음에 닫는 중괄호 2개 추가
# 줄 번호는 0-based이므로 225가 226번째 줄
if len(lines) > 226:
    # 226번째 줄 내용 확인
    if "parameters" in lines[225]:
        # 227번째 줄에 닫는 중괄호들 추가
        lines[226] = "                    }\n                })\n"
        
        print("✅ 수정 완료!")
        print(f"226번째 줄: {lines[225]}")
        print(f"227번째 줄 (새로 추가됨): {lines[226]}")
    else:
        print("❌ 예상과 다른 코드 구조입니다.")
        print(f"226번째 줄: {lines[225]}")
else:
    print("❌ 파일이 너무 짧습니다.")

# 파일 쓰기
with open("LocalAgentMCP/studio_server.py", "w", encoding="utf-8") as f:
    f.writelines(lines)

print("파일이 저장되었습니다.")
