# plugins/system_tools.py
# 시스템 제어 플러그인 (shell / process / os-level actions)

import os
import subprocess
import platform
import psutil

MCP_TOOLS = {}
INPUT_SCHEMAS = {}

# --------------------------------------------------------------
# system.shell (명령어 실행)
# --------------------------------------------------------------
def system_shell(command: str, cwd: str = None) -> str:
    """
    Executes a shell command and returns stdout + stderr.
    Supports PowerShell / CMD / Bash depending on OS.
    """
    shell_flag = True if platform.system() == "Windows" else False

    try:
        result = subprocess.run(
            command,
            shell=shell_flag,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        return f"[EXIT {result.returncode}]\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

    except Exception as e:
        return f"[ERROR] {e}"


MCP_TOOLS["system.shell"] = system_shell
INPUT_SCHEMAS["system.shell"] = {
    "type": "object",
    "properties": {
        "command": {"type": "string"},
        "cwd": {"type": "string"}
    },
    "required": ["command"]
}

# --------------------------------------------------------------
# system.ps (프로세스 목록)
# --------------------------------------------------------------
def system_ps() -> str:
    """
    Returns a list of running processes (PID, name, memory usage).
    """
    processes = []

    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            mem = proc.info['memory_info'].rss // (1024 * 1024)
            processes.append(f"PID {proc.info['pid']:6} | {mem:5}MB | {proc.info['name']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return "\n".join(processes)


MCP_TOOLS["system.ps"] = system_ps
INPUT_SCHEMAS["system.ps"] = {"type": "object", "properties": {}}

# --------------------------------------------------------------
# system.open_path (폴더 또는 파일 열기)
# --------------------------------------------------------------
def system_open_path(path: str) -> str:
    """
    Opens a file or folder using the OS default explorer.
    """
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])

        return f"[OK] opened: {path}"

    except Exception as e:
        return f"[ERROR] {e}"


MCP_TOOLS["system.open_path"] = system_open_path
INPUT_SCHEMAS["system.open_path"] = {
    "type": "object",
    "properties": {
        "path": {"type": "string"}
    },
    "required": ["path"]
}
