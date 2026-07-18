"""
Retriever — Tim kiem chunks lien quan (Batch norm + Hybrid).

Hybrid pipeline:
1. Neu hybrid_retriever da init -> dung hybrid search (dense + BM25 + reranker)
2. Neu khong -> dung vector_store search (dense-only, fallback)
3. Similarity threshold filtering
4. Deduplication
5. Context assembly cho LLM prompt
"""

import logging
from typing import Optional

from config import settings
from rag.vector_store import vector_store, SearchResult

logger = logging.getLogger("retriever")


class Retriever:
    """Retrieval module cho RAG pipeline."""

    def __init__(
        self,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ):
        self.top_k = top_k or settings.TOP_K
        self.similarity_threshold = similarity_threshold or settings.SIMILARITY_THRESHOLD
        self._hybrid_enabled = False

    def enable_hybrid(self):
        """Enable hybrid search neu co BM25 index."""
        try:
            from rag.hybrid_retriever import hybrid_retriever
            from rag.bm25_search import bm25_search
            if bm25_search.is_initialized:
                hybrid_retriever.initialize()
                self._hybrid_enabled = True
                logger.info("Hybrid retrieval enabled")
            else:
                logger.info("BM25 chua init -> dung dense-only")
        except Exception as e:
            logger.warning(f"Hybrid init failed: {e} -> dung dense-only")

    def retrieve(self, query: str) -> list[SearchResult]:
        """Tim kiem chunks lien quan.

        Priority:
        1. Hybrid search (dense + BM25 + reranker) neu enabled
        2. Vector store search (dense-only)
        3. Threshold filter
        4. Dedup
        """
        # Step 1: Search
        if self._hybrid_enabled:
            try:
                from rag.hybrid_retriever import hybrid_retriever
                raw_results = hybrid_retriever.search(query, top_k=self.top_k * 2)
            except Exception as e:
                logger.warning(f"Hybrid search failed: {e}")
                raw_results = vector_store.search(query, top_k=self.top_k * 2)
        else:
            raw_results = vector_store.search(query, top_k=self.top_k * 2)

        if not raw_results:
            return []

        # Step 2: Threshold filter
        filtered = [r for r in raw_results if r.score >= self.similarity_threshold]

        if not filtered:
            return []

        # Step 3: Dedup by text fingerprint
        seen_texts = set()
        deduplicated = []
        for result in filtered:
            fingerprint = result.chunk.text[:100].strip()
            if fingerprint not in seen_texts:
                seen_texts.add(fingerprint)
                deduplicated.append(result)

        return deduplicated[:self.top_k]

    def build_context(self, results: list[SearchResult]) -> str:
        if not results:
            return ""

        context_parts = []
        for i, result in enumerate(results, 1):
            chunk = result.chunk
            header = f"[Nguon {i}: {chunk.title}"
            if chunk.section_header:
                header += f" - {chunk.section_header}"
            header += f"] (Do lien quan: {result.score:.0%})"
            context_parts.append(f"{header}\n{chunk.text}")

        return "\n\n---\n\n".join(context_parts)

    def get_sources(self, results: list[SearchResult]) -> list[dict]:
        sources = []
        seen_titles = set()
        for result in results:
            title = result.chunk.title
            if title not in seen_titles:
                seen_titles.add(title)
                sources.append({"title": title, "url": result.chunk.source_url})
        return sources


# Singleton
retriever = Retriever()
