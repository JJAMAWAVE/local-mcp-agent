#!/usr/bin/env python3
"""들여쓰기 문제 수정"""

# 파일 읽기
with open("LocalAgentMCP/studio_server.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# 239번째 줄 (0-based로 238) 확인 및 수정
if len(lines) > 238:
    # 잘못된 들여쓰기를 수정
    if "try:" in lines[238]:
        lines[238] = "            try:\n"
        print(f"✅ 239번째 줄 들여쓰기 수정 완료!")
        print(f"수정 전 줄 내용: {repr(lines[238])}")
    else:
        print(f"❌ 예상과 다른 줄 내용: {lines[238]}")
else:
    print("❌ 파일이 너무 짧습니다.")

# 파일 쓰기
with open("LocalAgentMCP/studio_server.py", "w", encoding="utf-8") as f:
    f.writelines(lines)

print("파일이 저장되었습니다.")
