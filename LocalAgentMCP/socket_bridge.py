import asyncio
import websockets
import json
import logging
import win32file
import win32pipe
import concurrent.futures

# ▼▼▼ Render 주소 (그대로 유지) ▼▼▼
RENDER_WS_URL = "wss://mcp-relay-server.onrender.com/ws"

# Unity 파이프 설정
UNITY_COMMAND_PIPE = r"\\.\pipe\UnityAIAgentPipe"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SocketBridge")

# 블로킹 작업을 위한 스레드 풀
executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

def send_to_unity_sync(data):
    """Win32 API로 Unity 파이프에 명령 전송 (동기 함수)"""
    handle = None
    try:
        # 1. 파이프 연결
        handle = win32file.CreateFile(
            UNITY_COMMAND_PIPE,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0, None, win32file.OPEN_EXISTING, 0, None
        )
        
        # 2. 데이터 전송
        payload = (json.dumps(data) + "\n").encode("utf-8")
        win32file.WriteFile(handle, payload)
        win32file.FlushFileBuffers(handle) # 강제 전송
        
        # 3. 응답 대기
        resp_buffer = win32file.ReadFile(handle, 65536)[1]
        
        # 4. 핸들 닫기
        win32file.CloseHandle(handle)
        handle = None
        
        result = json.loads(resp_buffer.decode("utf-8").strip())
        return result

    except Exception as e:
        return {"error": f"Pipe Error: {str(e)}"}
    finally:
        if handle:
            try: win32file.CloseHandle(handle)
            except: pass

async def connect_to_cloud():
    """Render 서버와 영구 연결을 유지하며 데이터를 중계합니다."""
    loop = asyncio.get_running_loop()
    
    while True:
        try:
            logger.info(f"Connecting to Cloud: {RENDER_WS_URL} ...")
            async with websockets.connect(RENDER_WS_URL, ping_interval=20, ping_timeout=20) as websocket:
                logger.info("✅ Connected to Cloud! (Outbound Tunnel Established)")
                
                while True:
                    # 1. 클라우드(ChatGPT)로부터 명령 수신 대기
                    message = await websocket.recv()
                    logger.info(f"[Cloud Command] {message}")
                    
                    # 2. 받은 명령을 Unity 파이프로 전달 (별도 스레드에서 실행하여 소켓 끊김 방지)
                    # ★★★ 여기가 핵심 수정 사항입니다 ★★★
                    response = await loop.run_in_executor(executor, send_to_unity_sync, json.loads(message))
                    
                    logger.info(f"[Unity Response] {response}")

                    # 3. 실행 결과를 다시 클라우드로 보고
                    if response:
                        await websocket.send(json.dumps(response))

        except Exception as e:
            logger.error(f"Connection Error: {e}")
            logger.info("Retrying in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    # 윈도우 비동기 루프 정책 설정
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(connect_to_cloud())
    except KeyboardInterrupt:
        pass