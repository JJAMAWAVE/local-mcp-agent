#!/usr/bin/env python3
"""resource.update 도구 테스트"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from tools.file_tools import resource_write_handler

async def test_write():
    # 테스트 파라미터
    args = {
        "path": "C:\\local-mcp-agent\\LocalAgentMCP\\테스트 환키지롤.txt",
        "content": "안녕"
    }
    
    print(f"🧪 파일 쓰기 테스트 시작...")
    print(f"경로: {args['path']}")
    print(f"내용: {args['content']}")
    
    result = await resource_write_handler(args)
    
    print(f"\n결과: {result}")
    
    # 파일 존재 확인
    if os.path.exists(args['path']):
        print(f"✅ 파일이 성공적으로 생성되었습니다!")
        with open(args['path'], 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"파일 내용: {content}")
    else:
        print(f"❌ 파일이 생성되지 않았습니다!")

if __name__ == "__main__":
    asyncio.run(test_write())
