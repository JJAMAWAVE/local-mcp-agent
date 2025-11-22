# ================================================================
# unity_pipe_client.py (Refactored)
# ----------------------------------------------------------------
# 안정적인 Unity Windows Named Pipe 통신 클라이언트
# - 명령 파이프(COMMAND_PIPE)
# - 로그 파이프(LOG_PIPE)
# - 자동 재연결 / UTF-8 대응 / JSON-safe
# ================================================================

import json
import time
import threading
import win32file
import pywintypes

from typing import Callable, Optional, Dict

COMMAND_PIPE = r"\\.\pipe\UnityAIAgentPipe"
LOG_PIPE = r"\\.\pipe\UnityAIAgentLog"


class UnityPipeClient:
    """
    안정적인 Unity 파이프 클라이언트
    - Unity 명령 실행
    - Unity 로그 실시간 수신
    """

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        self.log_callback = log_callback
        self._start_log_thread()

    # ----------------------------------------------------------------------
    # PUBLIC: Unity 명령 실행
    # ----------------------------------------------------------------------
    def send(self, message: Dict, timeout: int = 30) -> Dict:
        """
        Unity로 JSON 명령 전송 후 응답을 기다린다.
        timeout: Unity가 응답할 때까지 기다리는 시간 (기본 30초)
        """

        handle = None
        try:
            # ====== 1) 파이프 연결 시도 ======
            try:
                handle = win32file.CreateFile(
                    COMMAND_PIPE,
                    win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                    0,
                    None,
                    win32file.OPEN_EXISTING,
                    0,
                    None
                )
            except pywintypes.error as e:
                if e.winerror == 2:
                    return {"success": False, "error": "Unity Pipe not found. (Is Unity running?)"}
                if e.winerror == 231:
                    return {"success": False, "error": "Unity Pipe busy. Previous operation stuck?"}
                return {"success": False, "error": f"Pipe Connect Error: {e}"}

            # ====== 2) 명령 JSON 직렬화 ======
            try:
                payload = (json.dumps(message, ensure_ascii=False) + "\n").encode("utf-8")
            except Exception as e:
                return {"success": False, "error": f"JSON Encode Error: {e}"}

            # ====== 3) Unity로 송신 ======
            win32file.WriteFile(handle, payload)
            win32file.FlushFileBuffers(handle)

            # ====== 4) 응답 블로킹 대기 ======
            start_time = time.time()

            while True:
                if time.time() - start_time > timeout:
                    return {"success": False, "error": f"Unity response timeout ({timeout}s)"}

                try:
                    result_bytes = win32file.ReadFile(handle, 65536)[1]
                    decoded = result_bytes.decode("utf-8").strip()

                    # 빈 데이터면 계속 대기
                    if not decoded:
                        time.sleep(0.05)
                        continue

                    # JSON 파싱
                    try:
                        return json.loads(decoded)
                    except:
                        return {"success": False, "error": f"Invalid JSON: {decoded}"}

                except Exception:
                    # 잠시 대기 후 재시도 (파이프가 바로 응답하지 않는 경우)
                    time.sleep(0.05)

        except Exception as e:
            return {"success": False, "error": f"Unexpected pipe error: {e}"}

        finally:
            if handle:
                try:
                    win32file.CloseHandle(handle)
                except:
                    pass

    # ----------------------------------------------------------------------
    # PUBLIC: 로그 콜백 설정
    # ----------------------------------------------------------------------
    def set_log_callback(self, callback: Callable[[str], None]):
        self.log_callback = callback

    # ----------------------------------------------------------------------
    # INTERNAL: 로그 수신 스레드 시작
    # ----------------------------------------------------------------------
    def _start_log_thread(self):
        t = threading.Thread(target=self._log_loop, daemon=True)
        t.start()

    # ----------------------------------------------------------------------
    # INTERNAL: Unity Log Listener Loop
    # ----------------------------------------------------------------------
    def _log_loop(self):
        """
        Unity 로그 파이프 계속 감시 스레드
        Unity가 꺼졌다 켜져도 자동 재연결됨
        """
        while True:
            try:
                handle = win32file.CreateFile(
                    LOG_PIPE,
                    win32file.GENERIC_READ,
                    0,
                    None,
                    win32file.OPEN_EXISTING,
                    0,
                    None
                )

                while True:
                    raw = win32file.ReadFile(handle, 65536)[1]
                    text = raw.decode("utf-8", errors="ignore").strip()

                    if text and self.log_callback:
                        self.log_callback(text)

            except:
                # Unity 로그 파이프가 없을 때
                time.sleep(1)
