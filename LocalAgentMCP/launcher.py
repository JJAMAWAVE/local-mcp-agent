import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import sys
import os
import psutil

# =================================================
# CONFIG
# =================================================
AGENT_SCRIPT = "agent_server.py"
LAUNCHER_PORT = 8888

app = FastAPI(title="MCP Agent Launcher (PowerShell Edition)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

agent_process = None

def find_existing_agent():
    """이미 실행 중인 agent_server.py 프로세스 찾기"""
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # 파이썬이면서 agent_server.py를 돌리는 놈 찾기
            if proc.info['pid'] != current_pid and \
               'python' in proc.info['name'] and \
               proc.info['cmdline'] and \
               any(AGENT_SCRIPT in arg for arg in proc.info['cmdline']):
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None

@app.get("/status")
def get_status():
    # 실제로 프로세스가 떠있는지 확인
    proc = find_existing_agent()
    if proc and proc.is_running():
        return {"status": "running", "pid": proc.pid}
    return {"status": "stopped"}

@app.post("/start")
def start_agent():
    global agent_process
    
    if get_status()["status"] == "running":
        return {"status": "error", "message": "Already running"}

    try:
        # [핵심 수정] PowerShell 새 창을 띄워서 실행 (-NoExit 옵션으로 창 유지)
        cmd = [
            "powershell", 
            "-NoExit", 
            "-Command", 
            f"python {AGENT_SCRIPT}; echo '--------------------------------'; echo 'Agent Stopped. Close this window to clean up.'"
        ]
        
        # 새 콘솔 창 생성 (CREATE_NEW_CONSOLE)
        agent_process = subprocess.Popen(
            cmd,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        return {"status": "success", "pid": agent_process.pid}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/stop")
def stop_agent():
    # 파워쉘로 띄우면 프로세스 트리가 복잡해져서, 
    # 이름(cmdline)으로 찾아서 죽이는게 가장 확실함
    proc = find_existing_agent()
    if proc:
        try:
            # 파이썬 프로세스 종료
            proc.terminate()
            # 혹시 모르니 파워쉘 창도 찾아서 닫을 수 있으면 좋지만, 
            # 일단 서버만 내려가면 됨.
            return {"status": "success", "message": "Stopped"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    return {"status": "error", "message": "Not running"}

if __name__ == "__main__":
    # 시작 전 기존 좀비 프로세스 청소
    existing = find_existing_agent()
    if existing:
        print(f"🧹 Cleaning up existing agent (PID: {existing.pid})...")
        existing.terminate()

    print(f"🚀 Launcher Online: http://localhost:{LAUNCHER_PORT}")
    print(f"👉 Please refresh dashboard.html")
    
    uvicorn.run(app, host="0.0.0.0", port=LAUNCHER_PORT)