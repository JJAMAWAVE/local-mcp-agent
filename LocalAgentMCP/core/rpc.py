# rpc.py
import logging
import asyncio
import time
from typing import Dict, Any

logger = logging.getLogger("RPC-Engine")

# -------------------------------------------------------------
# JSON-RPC 표준 응답 생성기
# -------------------------------------------------------------
def rpc_success(rpc_id, result):
    return {
        "jsonrpc": "2.0",
        "id": rpc_id,
        "result": {"content": [{"type": "text", "text": str(result)}]}
    }

def rpc_error(rpc_id, code, message):
    return {
        "jsonrpc": "2.0",
        "id": rpc_id,
        "error": {"code": code, "message": message}
    }


# -------------------------------------------------------------
# Tool 실행 Wrapper (sync/async 자동 처리 + 예외 핸들링)
# -------------------------------------------------------------
async def execute_tool(tool: Dict[str, Any], args: Dict[str, Any]):
    handler = tool.get("handler")

    if not handler:
        raise Exception("Tool has no handler()")

    # async
    if asyncio.iscoroutinefunction(handler):
        return await handler(args)

    # sync
    return handler(args)


# -------------------------------------------------------------
# Main RPC Dispatcher
# -------------------------------------------------------------
async def handle_rpc(body: Dict[str, Any], registry: Dict[str, Any]):
    rpc_id = body.get("id")
    method = body.get("method")
    params = body.get("params", {})
    version = body.get("jsonrpc")

    # ---------------------------------------------------------
    # JSON-RPC 기본 검증
    # ---------------------------------------------------------
    if version != "2.0":
        return rpc_error(rpc_id, -32600, "Invalid JSON-RPC version")

    if not method:
        return rpc_error(rpc_id, -32600, "Missing method")

    # ---------------------------------------------------------
    # 1) initialize
    # ---------------------------------------------------------
    if method == "initialize":
        logger.info("[RPC] initialize request")

        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "tools": {
                        name: {"name": name}
                        for name in registry.keys()
                    }
                },
                "serverInfo": {
                    "name": "LocalAIAgent",
                    "version": "2.0"
                }
            }
        }

    # ---------------------------------------------------------
    # 2) tools/list
    # ---------------------------------------------------------
    if method == "tools/list":
        logger.info("[RPC] tools/list received")

        tools_list = []
        for name, info in registry.items():
            tools_list.append({
                "name": name,
                "description": info.get("description", ""),
                "inputSchema": info.get("inputSchema", {})
            })

        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {"tools": tools_list}
        }

    # ---------------------------------------------------------
    # 3) tools/call
    # ---------------------------------------------------------
    if method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        logger.info(f"[RPC] tools/call → {tool_name}")

        if not tool_name:
            return rpc_error(rpc_id, -32602, "Tool name missing")

        if tool_name not in registry:
            return rpc_error(rpc_id, -32601, f"Tool not found: {tool_name}")

        tool = registry[tool_name]

        try:
            started = time.time()
            result = await execute_tool(tool, args)
            duration = time.time() - started

            logger.info(f"[RPC] Tool '{tool_name}' finished in {duration:.3f}s")
            return rpc_success(rpc_id, result)

        except Exception as e:
            logger.error(f"[RPC] Tool execution failed: {e}")
            return rpc_error(rpc_id, -32603, str(e))

    # ---------------------------------------------------------
    # Unknown Method
    # ---------------------------------------------------------
    return rpc_error(rpc_id, -32601, f"Unknown method: {method}")
