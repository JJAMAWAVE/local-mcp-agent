import requests
import json

url = "http://localhost:8123/rpc"
payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "fs.list_dir",
        "arguments": {
            "path": "C:/local-mcp-agent/LocalAgentMCP"
        }
    },
    "id": 1
}

try:
    response = requests.post(url, json=payload)
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
