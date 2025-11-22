import os
import fnmatch
import asyncio

# -------------------------------------------------------
# [내부 함수] 실제 I/O 처리
# -------------------------------------------------------
def _blocking_write(path: str, content: str):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

def _blocking_read(path: str):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

# -------------------------------------------------------
# [핸들러] AI의 말실수(path vs scope)를 커버하는 로직
# -------------------------------------------------------
async def resource_read_handler(args: dict):
    # AI가 path라고 하든 target_id라고 하든 다 받아줌
    path = args.get("target_id") or args.get("path")
    if not path or not os.path.exists(path):
        return {"status": "error", "message": "Target path not found."}
    try:
        data = await asyncio.to_thread(_blocking_read, path)
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def resource_write_handler(args: dict):
    path = args.get("target_id") or args.get("path")
    content = args.get("payload") or args.get("content") or ""
    
    try:
        await asyncio.to_thread(_blocking_write, path, content)
        return {"status": "success", "target_id": path}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def resource_batch_update_handler(args: dict):
    resources = args.get("resources", [])
    results = []
    success_count = 0
    for item in resources:
        path = item.get("target_id") or item.get("path")
        content = item.get("payload") or item.get("content") or ""
        try:
            await asyncio.to_thread(_blocking_write, path, content)
            results.append(f"[OK] {path}")
            success_count += 1
        except Exception as e:
            results.append(f"[FAIL] {path} : {str(e)}")
    return {"status": "success", "summary": f"Processed {len(resources)} files.", "details": results}

def resource_search_handler(args: dict):
    # [핵심 수정] scope가 없으면 path를 찾고, 그것도 없으면 에러
    directory = args.get("scope") or args.get("path")
    pattern = args.get("filter", "*.*")
    
    if not directory:
        return {"status": "error", "message": "Missing 'scope' or 'path' argument."}
    if not os.path.exists(directory):
        return {"status": "error", "message": f"Directory not found: {directory}"}

    results = []
    try:
        for root, dirs, files in os.walk(directory):
            for fname in files:
                if fnmatch.fnmatch(fname, pattern):
                    results.append(os.path.join(root, fname))
        # 결과가 너무 많으면 잘라서 반환 (렉 방지)
        if len(results) > 100:
            return {"status": "success", "count": len(results), "items": results[:100], "note": "Too many files, showing first 100"}
        return {"status": "success", "items": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# -------------------------------------------------------
# [툴 정의] 스키마 검문소를 대폭 완화함
# -------------------------------------------------------
TOOL_DEFINITIONS = {
    "resource.fetch": {
        "description": "Read file content.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_id": {"type": "string", "description": "File path"},
                "path": {"type": "string", "description": "Alias for target_id"}
            }
            # required를 제거하여 AI가 둘 중 하나만 보내도 통과되게 함
        },
        "handler": resource_read_handler
    },
    
    "resource.update": {
        "description": "Create or update a file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_id": {"type": "string"},
                "path": {"type": "string"},
                "payload": {"type": "string"},
                "content": {"type": "string"}
            }
        },
        "handler": resource_write_handler
    },

    "resource.batch_update": {
        "description": "Create multiple files at once.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "resources": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "content": {"type": "string"}
                        }
                    }
                }
            }
        },
        "handler": resource_batch_update_handler
    },

    "resource.list": {
        "description": "List files in a directory.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "scope": {"type": "string", "description": "Folder path to search"},
                "path": {"type": "string", "description": "Alias for scope"},
                "filter": {"type": "string"}
            }
            # [핵심] required: ["scope"] 를 삭제함! 
            # 이제 AI가 path라고 보내도 스키마 에러가 안 뜨고 핸들러로 넘어감.
        },
        "handler": resource_search_handler
    }
}