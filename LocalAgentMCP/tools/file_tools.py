# plugins/file_tools.py
# 파일 처리 플러그인 (읽기 / 쓰기 / 검색)

import os
import fnmatch

MCP_TOOLS = {}
INPUT_SCHEMAS = {}

# --------------------------------------------------------------
# file.read
# --------------------------------------------------------------
def file_read(path: str) -> str:
    """
    Reads the content of a file.
    """
    if not os.path.exists(path):
        return f"[ERROR] file not found: {path}"

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


MCP_TOOLS["file.read"] = file_read
INPUT_SCHEMAS["file.read"] = {
    "type": "object",
    "properties": {
        "path": {"type": "string"}
    },
    "required": ["path"]
}

# --------------------------------------------------------------
# file.write
# --------------------------------------------------------------
def file_write(path: str, content: str) -> str:
    """
    Writes content to a file (overwrite).
    """
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"[OK] wrote file: {path}"


MCP_TOOLS["file.write"] = file_write
INPUT_SCHEMAS["file.write"] = {
    "type": "object",
    "properties": {
        "path": {"type": "string"},
        "content": {"type": "string"}
    },
    "required": ["path", "content"]
}

# --------------------------------------------------------------
# file.search (glob-like pattern scan)
# --------------------------------------------------------------
def file_search(directory: str, pattern: str = "*.cs") -> str:
    """
    Search files by glob pattern.
    Useful for Unity scripts/assets scanning.
    """

    if not os.path.exists(directory):
        return f"[ERROR] directory not found: {directory}"

    results = []

    for root, dirs, files in os.walk(directory):
        for fname in files:
            if fnmatch.fnmatch(fname, pattern):
                results.append(os.path.join(root, fname))

    return "\n".join(results) if results else "[EMPTY] no files found"


MCP_TOOLS["file.search"] = file_search
INPUT_SCHEMAS["file.search"] = {
    "type": "object",
    "properties": {
        "directory": {"type": "string"},
        "pattern": {"type": "string"}
    },
    "required": ["directory"]
}
