"""
Web Search Service — Tích hợp DuckDuckGo search cho tính năng Agentic RAG.
Giúp AI tra cứu thông tin trên Internet khi không tìm thấy trong Knowledge Base.
"""

import logging
from duckduckgo_search import DDGS

logger = logging.getLogger("web_search")

def search_web(query: str, max_results: int = 3) -> str:
    """Tìm kiếm thông tin trên DuckDuckGo.
    
    Args:
        query: Câu truy vấn của người dùng.
        max_results: Số lượng kết quả tối đa cần lấy.
        
    Returns:
        Chuỗi context định dạng để đưa vào LLM Prompt.
    """
    try:
        logger.info(f"Đang tìm kiếm Web với từ khóa: '{query}'")
        
        # Thêm từ khóa bệnh viện để đảm bảo ngữ cảnh
        search_query = f"{query} Bệnh viện Tim Hà Nội"
        
        with DDGS() as ddgs:
            results = list(ddgs.text(search_query, max_results=max_results))
            
        if not results:
            return ""
            
        context_parts = []
        for i, res in enumerate(results, 1):
            title = res.get('title', 'No Title')
            body = res.get('body', '')
            link = res.get('href', '')
            
            context_parts.append(
                f"[Nguồn Internet {i}: {title}]\n"
                f"Nội dung: {body}\n"
                f"Link: {link}"
            )
            
        final_context = "\n\n---\n\n".join(context_parts)
        return final_context
        
    except Exception as e:
        logger.error(f"Lỗi khi tìm kiếm Web: {e}")
        return ""
