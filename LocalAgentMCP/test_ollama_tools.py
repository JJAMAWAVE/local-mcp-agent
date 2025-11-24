#!/usr/bin/env python3
"""Ollama 도구 호출 직접 테스트"""
import httpx
import json
import asyncio

async def test_ollama_tools():
    url = "http://localhost:11434/api/chat"
    
    # 테스트 도구 정의
    tools = [{
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Create a text file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"},
                    "content": {"type": "string", "description": "File content"}
                },
                "required": ["path", "content"]
            }
        }
    }]
    
    # 테스트 요청
    payload = {
        "model": "qwen2.5-coder:14b",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. When user asks to create a file, use the create_file tool."
            },
            {
                "role": "user",
                "content": "Create a file at C:\\test.txt with content 'Hello'"
            }
        ],
        "tools": tools,
        "stream": False
    }
    
    print("🧪 Ollama 도구 호출 테스트...")
    print(f"모델: {payload['model']}")
    print(f"도구: {tools[0]['function']['name']}")
    print()
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json=payload)
            result = resp.json()
            
            print("📨 응답:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # tool_calls 확인
            message = result.get("message", {})
            if "tool_calls" in message:
                print("\n✅ 도구 호출됨!")
                print(f"도구: {message['tool_calls']}")
            else:
                print("\n❌ 도구가 호출되지 않았습니다!")
                print(f"텍스트 응답만 받음: {message.get('content', '')[:200]}")
                
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    asyncio.run(test_ollama_tools())
