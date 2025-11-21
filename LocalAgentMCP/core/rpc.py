# rpc.py
import logging
import asyncio

logger = logging.getLogger("RPC")

async def handle_rpc(body, registry):
    rpc_id = body.get("id")
    method = body.get("method")
    params = body.get("params", {})
    version = body.get("jsonrpc")

    if version != "2.0":
        return {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid JSON-RPC version"}, "id": rpc_id}

    # ===== initialize =====
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2025-02-01",
                "capabilities": {
                    "tools": {name: {"name": name} for name in registry}
                },
                "serverInfo": {
                    "name": "LocalAIAgent",
                    "version": "1.0"
                }
            },
            "id": rpc_id
        }

    # ===== tools/list =====
    if method == "tools/list":
        tools_list = []
        for t in registry.values():
            tools_list.append({
                "name": t["name"],
                "description": t["description"],
                "inputSchema": t["inputSchema"]
            })

        return {
            "jsonrpc": "2.0",
            "result": {"tools": tools_list},
            "id": rpc_id
        }

    # ===== tools/call =====
    if method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name not in registry:
            return {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Tool not found"}, "id": rpc_id}

        fn = registry[tool_name]["execute"]

        try:
            if asyncio.iscoroutinefunction(fn):
                result = await fn(args)
            else:
                result = fn(args)

            return {
                "jsonrpc": "2.0",
                "result": {"content": [{"type": "text", "text": str(result)}]},
                "id": rpc_id
            }
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": rpc_id}

    return {"jsonrpc": "2.0", "error": {"code": -32601, "message": f"Unknown method {method}"}, "id": rpc_id}
