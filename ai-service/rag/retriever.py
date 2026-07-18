"""
Retriever — Tìm kiếm chunks liên quan từ vector store.

Bao gồm logic:
- Similarity threshold filtering
- Deduplication (cùng source)
- Context assembly cho LLM prompt
"""

from typing import Optional

from config import settings
from rag.vector_store import vector_store, SearchResult


class Retriever:
    """Retrieval module cho RAG pipeline."""

    def __init__(
        self,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ):
        self.top_k = top_k or settings.TOP_K
        self.similarity_threshold = similarity_threshold or settings.SIMILARITY_THRESHOLD

    def retrieve(self, query: str) -> list[SearchResult]:
        """Tìm kiếm chunks liên quan cho query.

        Args:
            query: Câu hỏi của người dùng

        Returns:
            Danh sách SearchResult đã filtered và deduplicated
        """
        # Search vector store
        raw_results = vector_store.search(query, top_k=self.top_k * 2)

        if not raw_results:
            return []

        # Filter by similarity threshold
        filtered = [r for r in raw_results if r.score >= self.similarity_threshold]

        if not filtered:
            # Never relax the confidence gate. In a hospital assistant, missing
            # evidence must lead to an explicit handoff rather than generation.
            return []

        # Deduplicate: giữ chunk tốt nhất từ mỗi source
        seen_texts = set()
        deduplicated = []
        for result in filtered:
            # Tạo fingerprint từ text (first 100 chars)
            fingerprint = result.chunk.text[:100].strip()
            if fingerprint not in seen_texts:
                seen_texts.add(fingerprint)
                deduplicated.append(result)

        # Limit to top_k
        return deduplicated[:self.top_k]

    def build_context(self, results: list[SearchResult]) -> str:
        """Xây dựng context string từ search results cho LLM prompt.

        Format:
        [Nguồn 1: Title]
        Content text...

        [Nguồn 2: Title]
        Content text...
        """
        if not results:
            return ""

        context_parts = []
        for i, result in enumerate(results, 1):
            chunk = result.chunk
            header = f"[Nguồn {i}: {chunk.title}"
            if chunk.section_header:
                header += f" — {chunk.section_header}"
            header += f"] (Độ liên quan: {result.score:.0%})"

            context_parts.append(f"{header}\n{chunk.text}")

        return "\n\n---\n\n".join(context_parts)

    def get_sources(self, results: list[SearchResult]) -> list[dict]:
        """Trích xuất danh sách sources từ results."""
        sources = []
        seen_titles = set()

        for result in results:
            title = result.chunk.title
            if title not in seen_titles:
                seen_titles.add(title)
                sources.append({
                    "title": title,
                    "url": result.chunk.source_url
                })

        return sources


# Singleton instance
retriever = Retriever()
