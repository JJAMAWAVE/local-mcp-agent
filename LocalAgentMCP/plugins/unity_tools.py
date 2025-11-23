import json
import logging
import time
import win32file
import win32pipe

logger = logging.getLogger("UnityTools")

PIPE_NAME = r"\\.\pipe\UnityAIAgentPipe"

def send_unity_message(args):
    """
    Sends a JSON message to Unity via Named Pipe.
    """
    method = args.get("method")
    params = args.get("params", {})
    
    if not method:
        return "Error: method is required"

    message = {
        "method": method,
        "params": params,
        "timestamp": time.time()
    }
    
    json_msg = json.dumps(message)
    
    try:
        # Connect to the pipe
        handle = win32file.CreateFile(
            PIPE_NAME,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0,
            None,
            win32file.OPEN_EXISTING,
            0,
            None
        )
        
        # Send message
        data = json_msg.encode('utf-8')
        win32file.WriteFile(handle, data)
        
        # Read response (optional, depending on protocol)
        # For now, we just assume fire-and-forget or simple ack if needed.
        # But usually named pipes are blocking or async. 
        # Let's try to read a response if Unity sends one back immediately.
        
        # win32file.ReadFile(handle, 4096) 
        
        win32file.CloseHandle(handle)
        return f"Sent to Unity: {json_msg}"
        
    except Exception as e:
        logger.error(f"Failed to connect to Unity Pipe: {e}")
        return f"Error connecting to Unity: {e}. Make sure Unity is running and the server is started."

TOOL_DEFINITIONS = {
    "unity.send_message": {
        "description": "Send a JSON message to Unity via Named Pipe",
        "inputSchema": {
            "type": "object",
            "properties": {
                "method": {"type": "string", "description": "Method name (e.g. CreateScript)"},
                "params": {"type": "object", "description": "Parameters for the method"}
            },
            "required": ["method"]
        },
        "handler": send_unity_message
    }
}
