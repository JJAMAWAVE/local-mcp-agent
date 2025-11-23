#!/usr/bin/env python3
"""도구 로더 테스트 스크립트"""
import sys
import os

# 경로 추가
sys.path.insert(0, os.path.dirname(__file__))

from tool_loader import load_all_tools

# 도구 로드
tools = load_all_tools()

print(f"\n✅ 총 {len(tools)}개의 도구가 로드되었습니다:\n")

for name in sorted(tools.keys()):
    desc = tools[name].get('description', 'No description')
    print(f"  • {name}: {desc}")

print("\n모든 도구가 정상적으로 로드되었습니다! ✅")
