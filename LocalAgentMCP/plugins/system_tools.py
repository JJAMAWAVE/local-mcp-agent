import subprocess
import logging

logger = logging.getLogger("SystemTools")

def run_command(args):
    command = args.get("command")
    cwd = args.get("cwd", ".")
    if not command:
        return "Error: Command is required"
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    except Exception as e:
        return f"Error running command: {e}"

TOOL_DEFINITIONS = {
    "system.run_command": {
        "description": "Run a shell command",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Command to run"},
                "cwd": {"type": "string", "description": "Current working directory"}
            },
            "required": ["command"]
        },
        "handler": run_command
    }
}
