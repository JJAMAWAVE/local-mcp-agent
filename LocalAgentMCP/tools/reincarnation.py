import os
import json
import glob
from datetime import datetime
from typing import Dict, Any

from tools.system_core import get_system_prompt

MEMORY_DIR = os.path.join(os.getcwd(), "memory_vault")

# ========================================================
# [NEW] 스마트 스캔 함수 (내용은 안 읽고 목록만 가져옴)
# ========================================================
def scan_directory_structure(path: str, depth: int = 2) -> str:
    """지정된 경로의 파일 구조를 트리 형태로 요약 반환"""
    if not os.path.exists(path):
        return f"❌ Path not found: {path}"
    
    tree_str = []
    base_level = path.count(os.sep)
    
    for root, dirs, files in os.walk(path):
        current_level = root.count(os.sep)
        if current_level - base_level >= depth:
            continue
            
        indent = "  " * (current_level - base_level)
        tree_str.append(f"{indent}📂 {os.path.basename(root)}/")
        
        for f in files:
            # 중요 파일만 표시 (설정 가능)
            if f.endswith(('.py', '.cs', '.md', '.txt', '.json')):
                tree_str.append(f"{indent}  📄 {f}")
                
    return "\n".join(tree_str) if tree_str else "(Empty Directory)"

# ========================================================
# 핸들러
# ========================================================
def save_soul(args: Dict[str, Any]) -> str:
    # (기존 코드와 동일)
    if not os.path.exists(MEMORY_DIR):
        os.makedirs(MEMORY_DIR)
    
    summary = args.get("summary", "No summary.")
    active_rules = args.get("active_rules", [])
    project_paths = args.get("project_paths", {})
    current_task_status = args.get("current_task_status", "Unknown")
    tech_stack = args.get("tech_stack", [])
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"soul_{timestamp}.json"
    
    data = {
        "timestamp": timestamp,
        "summary": summary,
        "active_rules": active_rules,
        "project_paths": project_paths,
        "current_task_status": current_task_status,
        "tech_stack": tech_stack
    }
    
    with open(os.path.join(MEMORY_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    with open(os.path.join(MEMORY_DIR, "soul_latest.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return "✅ [Soul Saved] 기억 백업 완료."


def resurrect(args: Dict[str, Any]) -> str:
    if not os.path.exists(MEMORY_DIR):
        os.makedirs(MEMORY_DIR)
        
    latest_path = os.path.join(MEMORY_DIR, "soul_latest.json")
    
    data = {}
    if os.path.exists(latest_path):
        with open(latest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    
    system_protocol = get_system_prompt()

    # -----------------------------------------------------
    # [핵심] 주요 자산 스캔 (부하 최소화 + 구조 인식)
    # -----------------------------------------------------
    
    # 1. Local Tools 구조
    tools_path = r"C:\local-mcp-agent\LocalAgentMCP\tools"
    tools_map = scan_directory_structure(tools_path, depth=1)

    # 2. Project Docs/Assets 구조
    project_path = r"C:\AshenWard"
    project_map = scan_directory_structure(project_path, depth=2)

    # 3. GitHub Info (URL만 제공, 내용은 필요시 fetch)
    github_info = (
        "Repository: https://github.com/JJAMAWAVE/mcp-relay-server/tree/main\n"
        "Note: Do NOT clone entire repo. Use `github.fetch_file` tool when code analysis is needed."
    )

    response_text = (
        f"{system_protocol}\n\n"
        f"##################################################\n"
        f"⚠️  SYSTEM REBOOT: KNOWLEDGE MAP LOADED  ⚠️\n"
        f"##################################################\n\n"
        f"🗺️ [RESOURCE MAP - I know where files are]\n\n"
        f"1️⃣ [MY TOOLS] ({tools_path})\n{tools_map}\n\n"
        f"2️⃣ [PROJECT WORKSPACE] ({project_path})\n{project_map}\n\n"
        f"3️⃣ [REMOTE SERVER REPO]\n{github_info}\n\n"
        f"==================================================\n"
        f"📂 [RESTORED CONTEXT]\n"
        f"- Last Task: {data.get('current_task_status', 'Ready')}\n"
        f"- Active Rules: {data.get('active_rules', [])}\n"
        f"- Tech Stack: {data.get('tech_stack', [])}\n\n"
        f"📢 [READY]\n"
        f"I have analyzed the file structures above.\n"
        f"Waiting for command."
    )
    return response_text

TOOL_DEFINITIONS = {
    "system.save_soul": {
        "description": "Save current context.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "active_rules": {"type": "array", "items": {"type": "string"}},
                "project_paths": {"type": "object"},
                "current_task_status": {"type": "string"},
                "tech_stack": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["summary", "current_task_status"]
        },
        "handler": save_soul
    },
    "system.resurrect": {
        "description": "Restore memory & Load file maps (Tools, Project, GitHub).",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
        "handler": resurrect
    }
}