import os
import logging

logger = logging.getLogger("FileTools")

def read_file(args):
    path = args.get("path")
    if not path or not os.path.exists(path):
        return f"Error: File not found: {path}"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(args):
    path = args.get("path")
    content = args.get("content")
    if not path:
        return "Error: Path is required"
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {e}"

def list_dir(args):
    path = args.get("path")
    if not path or not os.path.exists(path):
        return f"Error: Directory not found: {path}"
    try:
        items = os.listdir(path)
        return "\n".join(items)
    except Exception as e:
        return f"Error listing directory: {e}"

def make_dir(args):
    path = args.get("path")
    if not path:
        return "Error: Path is required"
    try:
        os.makedirs(path, exist_ok=True)
        return f"Successfully created directory {path}"
    except Exception as e:
        return f"Error creating directory: {e}"

TOOL_DEFINITIONS = {
    "fs.read_file": {
        "description": "Read content of a file",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute path to the file"}
            },
            "required": ["path"]
        },
        "handler": read_file
    },
    "fs.write_file": {
        "description": "Write content to a file",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute path to the file"},
                "content": {"type": "string", "description": "Content to write"}
            },
            "required": ["path", "content"]
        },
        "handler": write_file
    },
    "fs.list_dir": {
        "description": "List files in a directory",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute path to the directory"}
            },
            "required": ["path"]
        },
        "handler": list_dir
    },
    "fs.make_dir": {
        "description": "Create a directory",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute path to the directory"}
            },
            "required": ["path"]
        },
        "handler": make_dir
    }
}
