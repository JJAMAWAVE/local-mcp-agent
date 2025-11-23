from duckduckgo_search import DDGS
import json

TOOL_DEFINITIONS = {
    "web.search": {
        "handler": lambda args: search_web(args),
        "description": "Search the web for real-time information. Use this when you need up-to-date facts, news, or technical documentation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of results to return (default: 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
}

def search_web(args):
    query = args.get("query")
    max_results = args.get("max_results", 5)
    
    print(f"🌐 Searching Web: {query}")
    
    try:
        results = []
        with DDGS() as ddgs:
            # text() method returns a generator
            for r in ddgs.text(query, max_results=max_results):
                results.append(r)
        
        if not results:
            return "No results found."
            
        # Format results for the AI
        formatted = ""
        for i, res in enumerate(results):
            formatted += f"[{i+1}] {res.get('title', 'No Title')}\n"
            formatted += f"URL: {res.get('href', 'No URL')}\n"
            formatted += f"Snippet: {res.get('body', 'No Content')}\n\n"
            
        return formatted
        
    except Exception as e:
        return f"Error searching web: {str(e)}"
