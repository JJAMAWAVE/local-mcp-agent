# ===============================================================
# unity_bridge.py (리팩토링 버전)
# MCP → LocalAgent → Unity 파이프 표준 명령 포맷터
# ===============================================================

import json


class UnityBridge:

    @staticmethod
    def build(command: str, **kwargs) -> dict:
        """
        Build a standard Unity command packet.

        필수: command (예: 'create_object', 'modify_component', ...)
        선택: script_name, path, content, payload 등
        """

        packet = {
            "type": "unity_command",
            "command": command,
            "args": kwargs,  # 모든 추가 인자들 저장
        }

        return packet

    @staticmethod
    def prettify(data: dict) -> str:
        """Pretty JSON for debug logging."""
        return json.dumps(data, indent=2, ensure_ascii=False)
