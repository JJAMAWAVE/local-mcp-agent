#!/usr/bin/env python3
"""studio_server.py의 도구 실행 부분에 디버그 로그 추가"""

# 파일 읽기
with open("LocalAgentMCP/studio_server.py", "r", encoding="utf-8") as f:
    content = f.read()

# execute_tool 함수에 로그 추가
old_execute = '''async def execute_tool(tool_name, args):
    """툴 실행"""
    if tool_name not in TOOLS:
        return f"Error: Tool '{tool_name}' not found."
    
    try:
        handler = TOOLS[tool_name]["handler"]
        print(f"🔧 [Tool Run] {tool_name}")
        
        if asyncio.iscoroutinefunction(handler):
            result = await handler(args)
        else:
            result = await asyncio.to_thread(handler, args)
            
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"'''

new_execute = '''async def execute_tool(tool_name, args):
    """툴 실행"""
    if tool_name not in TOOLS:
        return f"Error: Tool '{tool_name}' not found."
    
    try:
        handler = TOOLS[tool_name]["handler"]
        print(f"🔧 [Tool Run] {tool_name}")
        print(f"📝 [Tool Args] {args}")
        
        if asyncio.iscoroutinefunction(handler):
            result = await handler(args)
        else:
            result = await asyncio.to_thread(handler, args)
        
        print(f"✅ [Tool Result] {result}")
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        error_msg = f"Error executing {tool_name}: {str(e)}"
        print(f"❌ [Tool Error] {error_msg}")
        return error_msg'''

content = content.replace(old_execute, new_execute)

# 파일 쓰기
with open("LocalAgentMCP/studio_server.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 디버그 로그가 추가되었습니다!")
