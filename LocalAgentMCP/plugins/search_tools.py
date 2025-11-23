# plugins/search_tools.py
from duckduckgo_search import DDGS
import logging

logger = logging.getLogger(__name__)

MCP_TOOLS = {}
INPUT_SCHEMAS = {}

def web_search(query: str, max_results: int = 3) -> str:
    """
    인터넷 검색(DuckDuckGo)을 통해 최신 정보를 가져옵니다.
    Unity 최신 기능, 에러 해결법, 날씨, 뉴스 등을 찾을 때 사용하세요.
    """
    logger.info(f"Searching Web: {query}")
    results = []
    
    try:
        with DDGS() as ddgs:
            # 텍스트 검색 실행
            search_gen = ddgs.text(query, max_results=max_results)
            for r in search_gen:
                title = r.get('title', 'No Title')
                link = r.get('href', 'No Link')
                body = r.get('body', 'No Content')
                results.append(f"Title: {title}\nLink: {link}\nSummary: {body}\n---")
                
        if not results:
            return "[검색 결과 없음] 다른 키워드로 시도해보세요."
            
        return "\n".join(results)

    except Exception as e:
        logger.error(f"Search failed: {e}")
        return f"[Error] 검색 중 오류 발생: {str(e)}"

# 툴 등록
MCP_TOOLS["web.search"] = web_search
INPUT_SCHEMAS["web.search"] = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "검색할 키워드 (예: Unity 6.0 새로운 기능)"},
        "max_results": {"type": "integer", "default": 3}
    },
    "required": ["query"]
}