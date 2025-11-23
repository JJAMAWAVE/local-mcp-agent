import os
import subprocess
import platform
import psutil

def system_shell_handler(args: dict):
    command = args.get("command", "")
    cwd = args.get("cwd", os.getcwd())

    # Windows 명령어 보정
    if platform.system() == "Windows":
        if not command.lower().startswith("cmd /c"):
            command = f"cmd /c {command}"

    try:
        # [핵심 수정] 한글 윈도우 호환성 (cp949)
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=False, # 바이너리로 받아서 수동 디코딩
        )
        
        # 수동 디코딩 (한글 깨짐 방지)
        try:
            stdout_txt = result.stdout.decode('cp949', errors='ignore')
            stderr_txt = result.stderr.decode('cp949', errors='ignore')
        except:
            stdout_txt = result.stdout.decode('utf-8', errors='ignore')
            stderr_txt = result.stderr.decode('utf-8', errors='ignore')

        return {
            "exitCode": result.returncode,
            "stdout": stdout_txt.strip(),
            "stderr": stderr_txt.strip()
        }

    except Exception as e:
        return {"error": str(e)}

def system_ps_handler(args: dict):
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            mem = proc.info['memory_info'].rss // (1024 * 1024)
            processes.append({"pid": proc.info['pid'], "name": proc.info['name'], "memoryMB": mem})
        except: continue
    return {"processes": processes[:30], "count": len(processes)}

def system_open_path_handler(args: dict):
    path = args.get("path")
    try:
        os.startfile(path)
        return {"status": "ok", "path": path}
    except Exception as e:
        return {"error": str(e)}

TOOL_DEFINITIONS = {
    "local_system.shell": {
        "description": "Run Shell Command",
        "inputSchema": { "type": "object", "properties": { "command": {"type": "string"} }, "required": ["command"] },
        "handler": system_shell_handler
    },
    "local_system.ps": {
        "description": "List Processes",
        "inputSchema": {"type": "object", "properties": {}},
        "handler": system_ps_handler
    },
    "local_system.open_path": {
        "description": "Open Path",
        "inputSchema": { "type": "object", "properties": { "path": {"type": "string"} }, "required": ["path"] },
        "handler": system_open_path_handler
    }
}