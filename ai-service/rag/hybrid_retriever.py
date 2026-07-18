"""
Hybrid Retriever — Dense + Sparse (BM25) -> RRF fusion -> Cross-encoder reranker.

Pipeline:
1. Dense search (ChromaDB/FAISS)
2. Sparse search (BM25)
3. RRF (Reciprocal Rank Fusion) ket qua
4. Cross-encoder rerank (optional, neu co model)
"""

import logging
from typing import Optional

from rag.vector_store import vector_store, SearchResult
from rag.bm25_search import bm25_search
from rag.chunker import Chunk

logger = logging.getLogger("hybrid_retriever")


# Cross-encoder reranker (optional)
try:
    from sentence_transformers import CrossEncoder
    RERANKER_AVAILABLE = True
except ImportError:
    RERANKER_AVAILABLE = False
    CrossEncoder = None


class HybridRetriever:
    """Hybrid search: dense + sparse -> RRF -> reranker (optional)."""

    def __init__(
        self,
        rrf_k: int = 60,
        dense_weight: float = 1.0,
        sparse_weight: float = 1.0,
        rerank_top_k: int = 10,
        use_reranker: bool = True
    ):
        self.rrf_k = rrf_k
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight
        self.rerank_top_k = rerank_top_k
        self.use_reranker = use_reranker
        self._reranker = None

    def initialize(self):
        """Init reranker model (optional)."""
        if self.use_reranker and RERANKER_AVAILABLE:
            try:
                # Model nho, chay duoc tren CPU
                self._reranker = CrossEncoder(
                    "cross-encoder/ms-marco-MiniLM-L-6-v2",
                    max_length=512
                )
                logger.info("Cross-encoder reranker ready: ms-marco-MiniLM-L-6-v2")
            except Exception as e:
                logger.warning(f"Reranker init failed: {e}. Bo qua reranker.")
                self._reranker = None
        else:
            logger.info("Reranker disabled (use_reranker=False)")

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Hybrid search pipeline.

        Steps:
        1. Dense search (lay top_k * 2)
        2. BM25 search (lay top_k * 2)
        3. RRF fusion
        4. Cross-encoder rerank (neu available)
        5. Return top_k final
        """
        if not vector_store.is_initialized:
            logger.warning("Vector store chua initialized")
            return []

        # Step 1: Dense search
        dense_results = vector_store.search(query, top_k=top_k * 3)
        logger.info(f"Dense search: {len(dense_results)} results")

        # Step 2: BM25 search
        bm25_results = bm25_search.search(query, top_k=top_k * 3)
        logger.info(f"BM25 search: {len(bm25_results)} results")

        # Step 3: RRF fusion
        fused = self._rrf_fuse(dense_results, bm25_results, top_k=top_k * 2)

        if not fused:
            return dense_results[:top_k] if dense_results else []

        # Step 4: Cross-encoder rerank (neu available)
        if self._reranker is not None:
            fused = self._rerank(query, fused)

        # Return top_k final
        for i, r in enumerate(fused):
            r.rank = i
        return fused[:top_k]

    def _rrf_fuse(
        self,
        dense: list[SearchResult],
        bm25: list[dict],
        top_k: int = 10
    ) -> list[SearchResult]:
        """Reciprocal Rank Fusion.

        RRF score = sum(1 / (k + rank_i)) cho moi item.
        """
        # Build score dict: text_hash -> RRF score
        rrf_scores: dict[str, dict] = {}

        # Dense results: rank = 1-based
        for rank, result in enumerate(dense, 1):
            text_key = result.chunk.text[:100]
            rrf_scores[text_key] = {
                "chunk": result.chunk,
                "score": 0.0,
                "dense_rank": rank,
                "bm25_rank": None
            }
            # Add dense RRF score
            rrf_scores[text_key]["score"] += self.dense_weight * (1.0 / (self.rrf_k + rank))

        # BM25 results
        for rank, result in enumerate(bm25, 1):
            text_key = result["text"][:100]
            if text_key in rrf_scores:
                rrf_scores[text_key]["score"] += self.sparse_weight * (1.0 / (self.rrf_k + rank))
                rrf_scores[text_key]["bm25_rank"] = rank
            else:
                # BM25-only result — create a temporary chunk
                meta = result.get("metadata", {})
                chunk = Chunk(
                    text=result["text"],
                    title=meta.get("title", ""),
                    source_url=meta.get("source_url", ""),
                    source_file=meta.get("source_file", ""),
                    chunk_index=meta.get("chunk_index", 0),
                    section_header=meta.get("section_header", ""),
                )
                rrf_scores[text_key] = {
                    "chunk": chunk,
                    "score": self.sparse_weight * (1.0 / (self.rrf_k + rank)),
                    "dense_rank": None,
                    "bm25_rank": rank
                }

        # Sort by RRF score
        sorted_items = sorted(rrf_scores.values(), key=lambda x: x["score"], reverse=True)

        results = []
        for item in sorted_items[:top_k]:
            results.append(SearchResult(
                chunk=item["chunk"],
                score=item["score"],
                rank=len(results)
            ))

        return results

    def _rerank(self, query: str, candidates: list[SearchResult]) -> list[SearchResult]:
        """Cross-encoder rerank."""
        if not candidates or not self._reranker:
            return candidates

        pairs = [(query, c.chunk.text) for c in candidates]
        try:
            scores = self._reranker.predict(pairs)
            for i, (candidate, score) in enumerate(zip(candidates, scores)):
                candidate.score = float(score)

            # Sort by reranker score
            candidates.sort(key=lambda x: x.score, reverse=True)
            logger.info(f"Reranked: top score={candidates[0].score:.4f}")
        except Exception as e:
            logger.warning(f"Rerank failed: {e}")

        return candidates


# Singleton
hybrid_retriever = HybridRetriever()
