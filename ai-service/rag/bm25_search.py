"""
BM25 Sparse Search — Tokenize tieng Viet + BM25Okapi ranking.

Su dung rank_bm25 library.
Tokenize: split theo whitespace + bo dau cau co ban cho tieng Viet.
"""

import re
import logging
from typing import Optional, Callable

from rank_bm25 import BM25Okapi

logger = logging.getLogger("bm25_search")


def _default_tokenizer(text: str) -> list[str]:
    """Tokenize co ban cho tieng Viet: lower, split, filter short tokens."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)  # Bo dau cau
    tokens = text.split()
    tokens = [t for t in tokens if len(t) >= 2]  # Bo token 1 ky tu
    return tokens


class BM25Search:
    """BM25 sparse retrieval cho RAG hybrid search."""

    def __init__(self, tokenizer: Optional[Callable] = None):
        self._bm25: Optional[BM25Okapi] = None
        self._corpus: list[str] = []
        self._metadata: list[dict] = []
        self._tokenizer = tokenizer or _default_tokenizer
        self.is_initialized = False

    def build_index(self, texts: list[str], metadatas: Optional[list[dict]] = None):
        """Build BM25 index tu corpus."""
        if not texts:
            logger.warning("Khong co texts de index BM25")
            return

        tokenized_corpus = [self._tokenizer(t) for t in texts]
        self._bm25 = BM25Okapi(tokenized_corpus)
        self._corpus = texts
        self._metadata = metadatas or [{} for _ in texts]
        self.is_initialized = True
        logger.info(f"BM25 index built: {len(texts)} documents")

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        """Tim kiem BM25, tra ve list of {index, score, text, metadata}."""
        if not self._bm25 or not self.is_initialized:
            logger.warning("BM25 chua initialized")
            return []

        tokenized_query = self._tokenizer(query)
        scores = self._bm25.get_scores(tokenized_query)

        # Lay top_k index
        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] <= 0:
                continue
            results.append({
                "index": idx,
                "score": float(scores[idx]),
                "text": self._corpus[idx],
                "metadata": self._metadata[idx] if idx < len(self._metadata) else {}
            })

        return results

    @property
    def total_docs(self) -> int:
        return len(self._corpus)


# Singleton
bm25_search = BM25Search()
