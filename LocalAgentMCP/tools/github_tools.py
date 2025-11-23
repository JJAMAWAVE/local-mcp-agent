# github_tools.py
# GitHub Raw Content Fetch Tool

import requests

def github_fetch_file(args: dict):
    """
    Fetch raw file content from a GitHub repository.
    
    Required args:
      - owner: GitHub user or org
      - repo: repository name
      - path: file path in repo
      - branch: (optional) default: main
    """
    owner = args.get("owner")
    repo = args.get("repo")
    path = args.get("path")
    branch = args.get("branch", "main")

    if not owner or not repo or not path:
        return {"error": "Required fields: owner, repo, path"}

    # RAW URL 생성
    raw_url = (
        f"https://raw.githubusercontent.com/"
        f"{owner}/{repo}/{branch}/{path}"
    )
    
    try:
        res = requests.get(raw_url, timeout=15)

        if res.status_code == 200:
            return {
                "success": True,
                "url": raw_url,
                "content": res.text
            }
        else:
            return {
                "success": False,
                "url": raw_url,
                "status": res.status_code,
                "error": f"Failed to fetch file (HTTP {res.status_code})"
            }

    except Exception as e:
        return {"success": False, "error": str(e)}


# =====================================================
# MCP TOOL REGISTRATION
# =====================================================
TOOL = {
    "name": "github.fetch_file",
    "description": "Fetch a raw file from a GitHub repository",
    "inputSchema": {
        "type": "object",
        "properties": {
            "owner": {"type": "string", "description": "GitHub username or organization"},
            "repo": {"type": "string", "description": "Repository name"},
            "path": {"type": "string", "description": "File path inside the repo"},
            "branch": {"type": "string", "description": "Branch name (default: main)"}
        },
        "required": ["owner", "repo", "path"]
    },
    "handler": github_fetch_file
}
