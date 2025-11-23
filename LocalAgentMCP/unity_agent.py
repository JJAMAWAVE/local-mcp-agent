import json
import time
import threading
import traceback
import win32file
import pywintypes

from ollama_client import OllamaClient


# =============================================================
#  CONFIG
# =============================================================
COMMAND_PIPE = r"\\.\pipe\UnityAIAgentPipe"
LOG_PIPE = r"\\.\pipe\UnityAIAgentLog"

llm = OllamaClient(model="qwen3-coder:30b")


# =============================================================
#  Unity Pipe Client (명령 전송 + 로그 수신)
# =============================================================
class UnityPipeClient:
    def __init__(self):
        self.log_callback = None
        self._start_log_thread()

    # ---------------------------------------------------------
    # Unity 명령 전송
    # ---------------------------------------------------------
    def send(self, data: dict, timeout=30):
        """Unity 명령 파이프에 JSON 전송하고 응답 반환"""
        handle = None
        try:
            # 1. 파이프 연결
            handle = win32file.CreateFile(
                COMMAND_PIPE,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0, None, win32file.OPEN_EXISTING, 0, None
            )

            # 2. JSON 전송
            payload = (json.dumps(data) + "\n").encode("utf-8")
            win32file.WriteFile(handle, payload)
            win32file.FlushFileBuffers(handle)

            # 3. 응답 대기
            result = win32file.ReadFile(handle, 65536)[1]
            return json.loads(result.decode("utf-8").strip())

        except pywintypes.error as e:
            if e.winerror == 2:
                return {"error": "Unity Pipe not found — Unity 꺼져있음"}
            if e.winerror == 231:
                return {"error": "Unity Pipe busy — 이전 연결이 잠김"}
            return {"error": f"Pipe Error: {e}"}

        except Exception as e:
            return {"error": f"UnityPipeClient Exception: {e}"}

        finally:
            if handle:
                try:
                    win32file.CloseHandle(handle)
                except:
                    pass

    # ---------------------------------------------------------
    # Unity 로그 수신 스레드 시작
    # ---------------------------------------------------------
    def _start_log_thread(self):
        t = threading.Thread(target=self._log_loop, daemon=True)
        t.start()

    # ---------------------------------------------------------
    # 로그 콜백 등록
    # ---------------------------------------------------------
    def set_log_callback(self, callback):
        self.log_callback = callback

    # ---------------------------------------------------------
    # Unity Log Pipe 읽기
    # ---------------------------------------------------------
    def _log_loop(self):
        while True:
            try:
                handle = win32file.CreateFile(
                    LOG_PIPE,
                    win32file.GENERIC_READ,
                    0, None, win32file.OPEN_EXISTING, 0, None
                )

                while True:
                    result, data = win32file.ReadFile(handle, 65536)
                    text = data.decode("utf-8", errors="replace").strip()

                    if text and self.log_callback:
                        self.log_callback(text)

            except Exception:
                time.sleep(1)
                continue


# =============================================================
#  LLM 기반 자동 오류 수정 기능
# =============================================================
class UnityAutoFixer:
    def __init__(self, unity_client: UnityPipeClient):
        self.unity = unity_client

    # ---------------------------------------------------------
    # Unity 컴파일 에러 분석 → C# 스크립트 재작성
    # ---------------------------------------------------------
    def fix_error(self, err: dict):
        try:
            err_msg = err.get("unity_error", "")
            script = err.get("script_name", "")
            path = err.get("file_path", "")

            if not script:
                print("[AutoFix] script_name 없음, 처리 불가")
                return

            print(f"\n[AutoFix] 컴파일 오류 감지 → {script}.cs")
            print(f"[Unity Error] {err_msg}")

            prompt = f"""
Unity C# Compile Error:
{err_msg}

File: {path}/{script}.cs

Fix the FULL script. Output ONLY the final full C# code.
NO commentary. NO markdown.
            """

            llm_resp = llm.generate(prompt)
            new_code = llm_resp.get("response", "")

            # Markdown 제거
            new_code = new_code.replace("```csharp", "").replace("```", "").strip()

            print("[AutoFix] Unity에 수정 적용 중...")

            res = self.unity.send({
                "command": "fix_script",
                "script_name": script,
                "path": path,
                "content": new_code
            })

            print(f"[AutoFix] 적용 결과: {res}")

        except Exception as e:
            print(f"[AutoFix] 처리 실패: {e}")
            traceback.print_exc()


# =============================================================
#  메인 통합 Unity Agent
# =============================================================
class UnityAgent:
    def __init__(self):
        self.unity = UnityPipeClient()
        self.autofix = UnityAutoFixer(self.unity)

        # Unity 로그 이벤트 등록
        self.unity.set_log_callback(self.handle_unity_log)

        print("=== Unity Agent Ready ===")

    # ---------------------------------------------------------
    # Unity 로그 처리
    # ---------------------------------------------------------
    def handle_unity_log(self, text: str):
        """Unity 로그 → 에러 감지 → 자동 코드 수정"""
        try:
            data = json.loads(text)

            # 컴파일 오류 감지
            if data.get("type") in ("CompilerError", "Exception"):
                self.autofix.fix_error(data)

        except json.JSONDecodeError:
            # 일반 로그는 무시
            pass

    # ---------------------------------------------------------
    # 수동 명령 테스트용 (옵션)
    # ---------------------------------------------------------
    def run_console(self):
        while True:
            try:
                cmd = input("명령 > ").strip()
                if not cmd:
                    continue

                payload = {
                    "command": "raw_prompt",
                    "text": cmd
                }

                res = self.unity.send(payload)
                print("[Unity 응답]", res)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print("Error:", e)


# =============================================================
# 실행
# =============================================================
if __name__ == "__main__":
    agent = UnityAgent()
    agent.run_console()
