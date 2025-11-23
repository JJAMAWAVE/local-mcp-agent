import os
import importlib
import logging
import sys
from typing import Dict, Any

logger = logging.getLogger("ToolLoader")

# plugins 폴더는 core 폴더의 상위 폴더(LocalAgentMCP)의 plugins 폴더임
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGINS_DIR = os.path.join(BASE_DIR, "plugins")

# sys.path에 BASE_DIR 추가하여 plugins 모듈 import 가능하게 함
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

def load_all_tools() -> Dict[str, Dict[str, Any]]:
    """
    Loads all MCP tool modules inside /plugins.
    Each module must define:

        TOOL_DEFINITIONS = {
            "tool.name": {
                "description": "...",
                "inputSchema": {...},
                "handler": function_reference
            }
        }

    Returns a merged tool registry.
    """
    registry: Dict[str, Dict[str, Any]] = {}

    if not os.path.isdir(PLUGINS_DIR):
        logger.warning(f"[ToolLoader] Plugins dir not found, creating: {PLUGINS_DIR}")
        os.makedirs(PLUGINS_DIR, exist_ok=True)
        return registry

    for filename in os.listdir(PLUGINS_DIR):
        if not filename.endswith(".py") or filename.startswith("_"):
            continue

        module_name = filename[:-3]
        module_path = f"plugins.{module_name}"

        try:
            module = importlib.import_module(module_path)
            importlib.reload(module) # Reload to ensure fresh code
        except Exception as e:
            logger.error(f"[ToolLoader] Failed to import {module_name}: {e}")
            continue

        # -----------------------------------------
        # TOOL_DEFINITIONS 검색
        # -----------------------------------------
        if not hasattr(module, "TOOL_DEFINITIONS"):
            logger.info(f"[ToolLoader] Skipped {module_name}: no TOOL_DEFINITIONS")
            continue

        tool_defs = getattr(module, "TOOL_DEFINITIONS")

        if not isinstance(tool_defs, dict):
            logger.error(f"[ToolLoader] Invalid TOOL_DEFINITIONS in {module_name}")
            continue

        # -----------------------------------------
        # 각 Tool 검증 및 등록
        # -----------------------------------------
        for tool_name, tool_data in tool_defs.items():
            if tool_name in registry:
                logger.warning(f"[ToolLoader] Duplicate tool name: {tool_name} (ignored)")
                continue

            handler = tool_data.get("handler")
            if not callable(handler):
                logger.error(f"[ToolLoader] Tool '{tool_name}' missing valid handler()")
                continue

            # inputSchema 기본값 보정
            schema = tool_data.get("inputSchema", {})
            if not isinstance(schema, dict):
                logger.warning(f"[ToolLoader] Fixing invalid inputSchema for {tool_name}")
                tool_data["inputSchema"] = {}

            registry[tool_name] = tool_data
            logger.info(f"[ToolLoader] Loaded tool: {tool_name}")

    logger.info(f"[ToolLoader] Total Tools Loaded: {len(registry)}")
    return registry
