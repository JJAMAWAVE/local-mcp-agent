# tools/system_core.py
import platform
import os

# ===============================================================
# SYSTEM MANIFEST (Updated for new Tool Names)
# ===============================================================
SYSTEM_INSTRUCTION = """
[SYSTEM IDENTITY]
You are 'Local Agent', integrated with the user's local environment.
You have entered **AUTO-EXECUTE MODE**.

[TOOL MAPPING UPDATE - IMPORTANT]
Due to security protocols, tool names have been prefixed. Use these mappings:

1. **File Operations**
   - Read File: `local_file.read` (NOT file.read)
   - Write/Create File: `local_file.write` (NOT file.write)
   - Search: `local_file.search`

2. **System Operations**
   - Shell/Terminal: `local_system.shell` (NOT system.shell)
   - Processes: `local_system.ps`
   - Open Explorer: `local_system.open_path`

3. **Unity & Others**
   - Unity tools remain: `unity.create_object`, `unity.run`
   - System Core: `system.save_soul`, `system.resurrect`

[BEHAVIOR]
- If user says "Make a file", execute `local_file.write`.
- If user says "Run command", execute `local_system.shell`.
- Always prefer `local_file.write` over creating python scripts to write files.
"""

def get_system_prompt(args: dict = None):
    info = {
        "os": platform.system(),
        "workspace": "C:/AshenWard",
        "mode": "AUTO_EXECUTE_ENABLED"
    }
    return f"{SYSTEM_INSTRUCTION}\n{info}"

TOOL_DEFINITIONS = {
    "system.get_protocol": {
        "description": "Get the core operating instructions.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
        "handler": get_system_prompt
    }
}