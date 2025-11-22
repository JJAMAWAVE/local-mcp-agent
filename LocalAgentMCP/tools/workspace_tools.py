# workspace_tools.py
# -------------------------------------------------------------------
# Local Workspace Engine
# - 자동 폴더 생성
# - 전체 프로젝트 재귀 스캔
# - 코드/문서/텍스트 JSON 로딩
# - ChatGPT 분석용 데이터 제공
# -------------------------------------------------------------------

import os
import json
import time
from datetime import datetime

ROOT = r"C:/AshenWard"
DIR_HISTORY = os.path.join(ROOT, "gpt_history")
DIR_DOCS = os.path.join(ROOT, "gpt_docs")
DIR_IMAGES = os.path.join(ROOT, "gpt_images")
DIR_BACKUP = os.path.join(ROOT, "gpt_backups")
DIR_LOGS = os.path.join(ROOT, "gpt_logs")
DIR_WORKSPACE = os.path.join(ROOT, "gpt_workspace")

ALL_FOLDERS = [
    ROOT,
    DIR_HISTORY,
    DIR_DOCS,
    DIR_IMAGES,
    DIR_BACKUP,
    DIR_LOGS,
    DIR_WORKSPACE
]

# ------------------------------------------------------------
# 1. 폴더 자동 생성
# ------------------------------------------------------------
def ensure_workspace():
    for folder in ALL_FOLDERS:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
    return {"status": "ok", "root": ROOT, "folders": ALL_FOLDERS}


# ------------------------------------------------------------
# 2. 전체 폴더 재귀 스캔
# ------------------------------------------------------------
def scan_folder(path: str):
    """
    특정 폴더 내부 전체 구조를 재귀적으로 스캔
    반환값:
    {
        "files":[ full_path ],
        "folders":[ full_path ]
    }
    """
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return {"error": f"Path not found: {path}"}

    all_files = []
    all_dirs = []

    for root, dirs, files in os.walk(path):
        for d in dirs:
            all_dirs.append(os.path.join(root, d))
        for f in files:
            all_files.append(os.path.join(root, f))

    return {
        "root": path,
        "folder_count": len(all_dirs),
        "file_count": len(all_files),
        "folders": all_dirs,
        "files": all_files
    }


# ------------------------------------------------------------
# 3. 폴더 전체 내용 로딩 (코드/텍스트)
# ------------------------------------------------------------
TEXT_EXT = [
    ".txt", ".py", ".cs", ".json", ".md",
    ".shader", ".cpp", ".h", ".js", ".ts",
    ".xml", ".yaml", ".yml", ".ini"
]

def load_project_files(path: str):
    """
    프로젝트 전체 파일 로딩 → JSON 반환
    """
    scan = scan_folder(path)
    if "error" in scan:
        return scan

    files = scan["files"]
    result = {}

    for f in files:
        ext = os.path.splitext(f)[1].lower()
        if ext in TEXT_EXT:
            try:
                with open(f, "r", encoding="utf-8", errors="ignore") as fp:
                    result[f] = fp.read()
            except Exception as e:
                result[f] = f"[ERROR] Cannot read file: {e}"

    return {
        "project_root": path,
        "total_files": len(result),
        "loaded_files": result
    }


# ------------------------------------------------------------
# 4. 워크스페이스 파일 저장 API
# ------------------------------------------------------------
def save_to_workspace(filename: str, content: str):
    ensure_workspace()

    safe_name = filename.replace(":", "_").replace("/", "_").replace("\\", "_")
    path = os.path.join(DIR_WORKSPACE, safe_name)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return {"status": "saved", "path": path}


# ------------------------------------------------------------
# 5. 백업(버전 관리)
# ------------------------------------------------------------
def backup_file(original_path: str):
    if not os.path.exists(original_path):
        return {"error": "file not found"}

    ensure_workspace()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = os.path.basename(original_path)
    backup_path = os.path.join(DIR_BACKUP, f"{ts}_{fname}")

    try:
        with open(original_path, "rb") as src:
            with open(backup_path, "wb") as dst:
                dst.write(src.read())
        return {"status": "backup_ok", "backup": backup_path}
    except Exception as e:
        return {"error": str(e)}


# ------------------------------------------------------------
# 6. MCP 등록용 구조체
# ------------------------------------------------------------
TOOL = {
    "name": "workspace",
    "description": "Local workspace management (scan folders, read project files, save, backup)",
    "inputSchema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["init", "scan", "load", "save", "backup"]
            },
            "path": {"type": "string"},
            "filename": {"type": "string"},
            "content": {"type": "string"}
        },
        "required": ["action"]
    },
    "handler": lambda args: run_workspace_action(args)
}


# ------------------------------------------------------------
# 7. Dispatcher
# ------------------------------------------------------------
def run_workspace_action(args):
    action = args.get("action")

    if action == "init":
        return ensure_workspace()

    if action == "scan":
        return scan_folder(args.get("path"))

    if action == "load":
        return load_project_files(args.get("path"))

    if action == "save":
        return save_to_workspace(args.get("filename"), args.get("content"))

    if action == "backup":
        return backup_file(args.get("path"))

    return {"error": "Unknown action"}
