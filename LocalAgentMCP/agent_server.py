import asyncio
import json
import logging
import os
import subprocess
import websockets
from typing import Dict, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tool_loader import load_all_tools

# ==========================================================
# LOGGING & CONFIG
# ==========================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("LocalAgent")

RENDER_URL = "wss://mcp-relay-server.onrender.com/ws"
SERVER_VERSION = "1.0.8" # Fixed: Batch & Async I/O Support
PORT = 8123
FATIGUE_LIMIT = 30 
tool_usage_count = 0

# ==========================================================
# UTILS
# ==========================================================
def free_port(port: int):
    try:
        subprocess.run(f"taskkill /F /IM uvicorn.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass

TOOLS = load_all_tools()
render_ws: Optional[websockets.WebSocketClientProtocol] = None

app = FastAPI(title="Local MCP Agent", version=SERVER_VERSION)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "running", "connected": render_ws is not None}

# ==========================================================
# TOOL SYNC
# ==========================================================
async def sync_tools():
    try:
        tools_map = {}
        for name, data in TOOLS.items():
            tools_map[name] = {
                "description": data.get("description", ""),
                "inputSchema": data.get("inputSchema", {})
            }
        
        msg = {
            "id": "__sync_tools__",
            "type": "sync_response",
            "tools": tools_map 
        }
        
        await relay_send(msg)
        logger.info(f"[Sync] Sent {len(tools_map)} tools.")
    except Exception as e:
        logger.error(f"[Sync] Failed: {e}")

# ==========================================================
# MESSAGE HANDLER (안전장치 강화)
# ==========================================================
async def handle_relay_message(raw: str):
    global tool_usage_count
    try:
        payload = json.loads(raw)
    except: return # JSON 파싱 에러는 무시

    # 1. Sync
    if payload.get("id") == "__sync_tools__" or payload.get("type") == "sync_request":
        await sync_tools()
        return

    # 2. Tool Execution
    rpc_id = payload.get("id")
    tool = payload.get("tool")
    args = payload.get("args", {})

    if not tool: return 

    if tool not in TOOLS:
        await relay_send({"id": rpc_id, "error": f"Unknown tool: {tool}"})
        return

    if tool == "system.resurrect": tool_usage_count = 0
    else: tool_usage_count += 1
    
    logger.info(f"🚀 [EXEC] {tool}")

    try:
        handler = TOOLS[tool]["handler"]
        
        # 비동기 핸들러 지원 (파일 쓰기 중 핑 끊김 방지)
        if asyncio.iscoroutinefunction(handler):
            result = await handler(args)
        else:
            # 동기 핸들러라도 별도 스레드에서 실행하여 메인 루프 보호
            result = await asyncio.to_thread(handler, args)

        if tool_usage_count >= FATIGUE_LIMIT:
            warning = "\n[SYSTEM] Context full. Recommend '[환생]'."
            if isinstance(result, dict): result["_note"] = warning
            elif isinstance(result, str): result += warning
            
        await relay_send({"id": rpc_id, "result": result})
        logger.info(f"✅ [DONE] {tool}")

    except Exception as e:
        logger.error(f"❌ [TOOL ERR] {tool}: {e}")
        await relay_send({"id": rpc_id, "error": str(e)})

async def relay_send(data: dict):
    if render_ws:
        try: await render_ws.send(json.dumps(data, ensure_ascii=False))
        except Exception as e: logger.error(f"Send Fail: {e}")

# ==========================================================
# CONNECTION LOOP (절대 죽지 않는 루프)
# ==========================================================
async def connect_to_render():
    global render_ws
    while True:
        try:
            logger.info(f"🔌 Connecting to {RENDER_URL} ...")
            
            # [핵심 수정] ping_timeout을 300초(5분)로 늘려 대용량 파일 생성 중 끊김 방지
            # max_size=None으로 설정하여 긴 코드(페이로드) 수신 허용
            async with websockets.connect(
                RENDER_URL, 
                ping_interval=10, 
                ping_timeout=300, 
                max_size=None
            ) as ws:
                render_ws = ws
                logger.info("🔗 Connected! Syncing...")
                await sync_tools()

                async for message in ws:
                    try:
                        await handle_relay_message(message)
                    except Exception as e:
                        logger.error(f"⚠️ Message Handling Error: {e}")
        
        except Exception as e:
            logger.warning(f"💔 Disconnected: {e}")
            render_ws = None
        
        logger.info("🔄 Reconnecting in 2 seconds...")
        await asyncio.sleep(2)

@app.on_event("startup")
async def startup_event():
    logger.info("=== Local Agent Started (Fixed Batch/Async) ===")
    asyncio.create_task(connect_to_render())

if __name__ == "__main__":
    free_port(PORT)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)