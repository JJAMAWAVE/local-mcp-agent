import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import asyncio
import httpx
from tool_loader import load_all_tools

# ================= CONFIG =================
PORT = 8000
OLLAMA_URL = "http://localhost:11434/api/chat"
CONFIG_FILE = "ai_config.json"

app = FastAPI(title="Local AI Studio")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# 로컬 툴 로드 (우리가 만든 파일/유니티 제어 툴)
TOOLS = load_all_tools()

# 모델 설정 로드
def get_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# ================= TOOL EXECUTOR =================
async def execute_tool(tool_name, args):
    if tool_name not in TOOLS:
        return f"Error: Tool '{tool_name}' not found."
    
    try:
        handler = TOOLS[tool_name]["handler"]
        print(f"🔧 [Tool Run] {tool_name} with {args}")
        if asyncio.iscoroutinefunction(handler):
            result = await handler(args)
        else:
            result = await asyncio.to_thread(handler, args)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"

# ================= API & WEBSOCKET =================
@app.get("/")
async def get_ui():
    with open("studio.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/models")
async def list_models():
    return get_config().get("models", {})

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    history = [] # 대화 문맥 유지
    
    try:
        while True:
            data = await websocket.receive_json()
            user_msg = data.get("message")
            model_key = data.get("model", "fast_coding")
            
            config = get_config()
            model_name = config["models"][model_key]["name"]
            sys_prompt = config.get("system_prompt", "")

            # 1. 사용자 메시지 추가
            history.append({"role": "user", "content": user_msg})
            
            # 2. 도구 정의 (Ollama 포맷)
            ollama_tools = []
            for name, info in TOOLS.items():
                ollama_tools.append({
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": info.get("description", ""),
                        "parameters": info.get("inputSchema", {})
                    }
                })

            # 3. Ollama 호출 (스트리밍 아님 - 툴 사용 판단을 위해)
            payload = {
                "model": model_name,
                "messages": [{"role": "system", "content": sys_prompt}] + history,
                "tools": ollama_tools,
                "stream": False
            }

            # UI에 "생각 중..." 표시
            await websocket.send_json({"type": "status", "text": "🤔 AI가 생각 중입니다..."})

            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(OLLAMA_URL, json=payload)
                resp_json = resp.json()
                ai_msg = resp_json.get("message", {})

                # 4. 툴 사용 여부 확인
                if ai_msg.get("tool_calls"):
                    # AI가 도구를 쓰겠다고 함
                    history.append(ai_msg) # AI의 의도를 기록
                    
                    for tool_call in ai_msg["tool_calls"]:
                        fn = tool_call["function"]
                        t_name = fn["name"]
                        t_args = fn["arguments"]
                        
                        await websocket.send_json({"type": "status", "text": f"🛠️ 도구 실행 중: {t_name}..."})
                        
                        # 도구 실행!
                        tool_result = await execute_tool(t_name, t_args)
                        
                        # 결과 기록
                        history.append({
                            "role": "tool",
                            "content": tool_result,
                        })
                    
                    # 5. 도구 결과를 바탕으로 최종 답변 생성 요청
                    payload["messages"] = [{"role": "system", "content": sys_prompt}] + history
                    del payload["tools"] # 최종 답변 땐 툴 끔 (무한 루프 방지)
                    
                    final_resp = await client.post(OLLAMA_URL, json=payload)
                    final_msg = final_resp.json()["message"]["content"]
                    
                    history.append({"role": "assistant", "content": final_msg})
                    await websocket.send_json({"type": "answer", "text": final_msg})

                else:
                    # 도구 안 쓰고 바로 대답함
                    content = ai_msg.get("content", "")
                    history.append({"role": "assistant", "content": content})
                    await websocket.send_json({"type": "answer", "text": content})

    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    # uvicorn studio_server:app --reload
    uvicorn.run(app, host="0.0.0.0", port=PORT)