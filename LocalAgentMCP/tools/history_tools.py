# tools/history_tools.py
# Save ChatGPT conversation logs locally

import os
from datetime import datetime

HISTORY_BASE_PATH = r"C:\AshenWard\Documents\gpt_history"

def save_history_local(args: dict):
    """
    Save chat history text into a local folder.
    args:
        title: file title (optional)
        content: text content (required)
    """
    title = args.get("title", "chat_history")
    content = args.get("content", "")

    if not content:
        return {"error": "content is required"}

    # Ensure directory exists
    if not os.path.exists(HISTORY_BASE_PATH):
        os.makedirs(HISTORY_BASE_PATH)

    # Final filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_title = title.replace(" ", "_")
    filename = f"{timestamp}_{safe_title}.txt"

    file_path = os.path.join(HISTORY_BASE_PATH, filename)

    # Write file (UTF-8, Korean-safe)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return {
        "status": "ok",
        "path": file_path,
        "bytes": len(content)
    }


# ------------------------------------------------------------
# MCP Tool Definition
# ------------------------------------------------------------
TOOL_DEFINITIONS = {
    "history.save.local": {
        "description": "Save conversation history into a local folder",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["content"]
        },
        "handler": save_history_local
    }
}
