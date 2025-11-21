# unity_bridge.py
import json

class UnityBridge:
    @staticmethod
    def format_command(command, script_name="", path="", content=""):
        return {
            "command": command,
            "script_name": script_name,
            "path": path,
            "content": content
        }

    @staticmethod
    def pretty(json_dict):
        return json.dumps(json_dict, indent=2, ensure_ascii=False)
