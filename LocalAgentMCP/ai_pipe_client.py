import json
import threading
import time
import sys
import win32file
import pywintypes

COMMAND_PIPE = r"\\.\pipe\UnityAIAgentPipe"
LOG_PIPE = r"\\.\pipe\UnityAIAgentLog"

class UnityPipeClient:
    def __init__(self):
        self.log_callback = None
        self.start_log_listener()

    def send(self, message: dict, timeout=30):
        """명령 파이프로 JSON 전송 및 대기 표시"""
        handle = None
        try:
            # 1. 연결 시도
            handle = win32file.CreateFile(
                COMMAND_PIPE,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0, None, win32file.OPEN_EXISTING, 0, None
            )
            
            # 2. 데이터 전송
            payload = (json.dumps(message) + "\n").encode("utf-8")
            win32file.WriteFile(handle, payload)
            
            # ★★★ 핵심 수정: 버퍼 강제 비우기 (데이터 밀어넣기) ★★★
            win32file.FlushFileBuffers(handle)
            
            print("   [Pipe] Unity 응답 대기 중...", end="", flush=True)
            
            # 3. 수신 (Unity 처리 대기)
            # Unity가 처리할 때까지 블로킹됨
            resp_buffer = win32file.ReadFile(handle, 65536)[1]
            
            print(" 완료!")
            
            win32file.CloseHandle(handle)
            handle = None
            
            return json.loads(resp_buffer.decode("utf-8").strip())

        except pywintypes.error as e:
            if e.winerror == 2: 
                return {"success": False, "error": "Unity Pipe not found. (Unity is OFF?)"}
            if e.winerror == 231: 
                return {"success": False, "error": "Unity Pipe is busy. (Previous connection stuck?)"}
            return {"success": False, "error": f"Pipe Error: {e}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if handle:
                try: win32file.CloseHandle(handle)
                except: pass

    def start_log_listener(self, callback=None):
        if callback: self.log_callback = callback
        t = threading.Thread(target=self._log_loop, daemon=True)
        t.start()

    def set_log_callback(self, callback):
        self.log_callback = callback

    def _log_loop(self):
        while True:
            try:
                handle = win32file.CreateFile(
                    LOG_PIPE, win32file.GENERIC_READ, 0, None, win32file.OPEN_EXISTING, 0, None
                )
                while True:
                    data = win32file.ReadFile(handle, 65536)[1]
                    line = data.decode("utf-8").strip()
                    if line and self.log_callback: self.log_callback(line)
            except:
                time.sleep(1)