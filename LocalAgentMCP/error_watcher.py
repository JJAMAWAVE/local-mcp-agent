import json
import threading
import time
import traceback
from ai_pipe_client import UnityPipeClient
from ollama_client import OllamaClient as LocalAIClient # 이름 호환

unity = UnityPipeClient()
llm = LocalAIClient(model="qwen3-coder:30b")

def fix_error_with_llm(error_json):
    """에러 정보를 기반으로 수정된 코드 생성"""
    err_msg = error_json.get("unity_error", "")
    script = error_json.get("script_name", "")
    path = error_json.get("file_path", "")
    
    print(f"\n[AutoFix] Error Detected in {script}.cs: {err_msg}")

    # 1. 파일 내용 읽기 (선택 사항, 현재는 덮어쓰기 위주)
    # current_code = unity.send({"command": "read_file", "path": f"{path}/{script}.cs"})

    prompt = f"""
    Unity C# Compile Error:
    {err_msg}
    
    File: {path}/{script}.cs
    
    Fix the error and provide the FULL corrected C# script.
    Output ONLY the code. No markdown.
    """
    
    print("[AutoFix] Asking LLM for fix...")
    fixed_code = llm.generate(prompt).get("response", "")
    
    if not fixed_code:
        print("[AutoFix] LLM failed to generate code.")
        return

    # Markdown 제거
    fixed_code = fixed_code.replace("```csharp", "").replace("```", "").strip()

    # 2. Unity에 수정 적용
    print("[AutoFix] Sending fix to Unity...")
    res = unity.send({
        "command": "fix_script",
        "script_name": script,
        "path": path,
        "content": fixed_code
    })
    print(f"[AutoFix] Result: {res}")

def watch_loop():
    print("[Watcher] Listening for Unity Logs...")
    # 로그 파이프 리스너 시작 (UnityPipeClient 내부 스레드 사용)
    unity.start_log_listener(callback=on_log_received)
    
    while True:
        time.sleep(1) # 메인 스레드 유지

def on_log_received(log_line):
    try:
        data = json.loads(log_line)
        # 컴파일 에러인지 확인
        if data.get("type") == "CompilerError" or "error CS" in data.get("unity_error", ""):
            fix_error_with_llm(data)
    except json.JSONDecodeError:
        pass # 일반 로그 무시
    except Exception as e:
        print(f"[Watcher] Error: {e}")

def start_error_watcher():
    t = threading.Thread(target=watch_loop, daemon=True)
    t.start()