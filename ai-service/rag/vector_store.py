"""
Vector Store — FAISS-based vector storage và similarity search.

Sử dụng FAISS Flat Index (đơn giản, chính xác tuyệt đối).
Phù hợp cho dataset nhỏ (~100-500 chunks).
"""

import numpy as np
import faiss
from typing import Optional
from dataclasses import dataclass

from rag.chunker import Chunk
from rag.embedder import embedder


@dataclass
class SearchResult:
    """Kết quả tìm kiếm từ vector store."""
    chunk: Chunk
    score: float  # Cosine similarity (0-1)
    rank: int


class VectorStore:
    """FAISS vector store cho RAG retrieval."""

    def __init__(self):
        self.index: Optional[faiss.IndexFlatIP] = None  # Inner Product (cosine sim)
        self.chunks: list[Chunk] = []
        self.is_initialized: bool = False

    def build_index(self, chunks: list[Chunk]):
        """Xây dựng FAISS index từ danh sách chunks.

        Steps:
        1. Tạo embeddings cho tất cả chunks
        2. Normalize vectors (cho cosine similarity)
        3. Build FAISS index
        """
        if not chunks:
            print("⚠️  Không có chunks để index")
            return

        self.chunks = chunks

        # Tạo embeddings cho tất cả chunks
        print(f"🔄 Đang tạo embeddings cho {len(chunks)} chunks...")
        texts = [chunk.embedding_text for chunk in chunks]
        embeddings = embedder.embed_texts(texts)

        if embeddings.size == 0:
            print("❌ Embedding failed — không có vectors")
            return

        # Normalize cho cosine similarity
        faiss.normalize_L2(embeddings)

        # Build FAISS Flat Inner Product index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)

        self.is_initialized = True
        print(f"✅ FAISS index built: {self.index.ntotal} vectors, dim={dimension}")

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Tìm kiếm chunks tương tự nhất với query.

        Args:
            query: Câu hỏi của người dùng
            top_k: Số kết quả trả về

        Returns:
            Danh sách SearchResult sorted by score (cao → thấp)
        """
        if not self.is_initialized:
            print("⚠️  Vector store chưa initialized")
            return []

        # Embed query
        query_vector = embedder.embed_query(query)
        query_vector = query_vector.reshape(1, -1).astype(np.float32)
        faiss.normalize_L2(query_vector)

        # Search
        top_k = min(top_k, len(self.chunks))
        scores, indices = self.index.search(query_vector, top_k)

        results = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < 0 or idx >= len(self.chunks):
                continue
            results.append(SearchResult(
                chunk=self.chunks[idx],
                score=float(score),
                rank=rank
            ))

        return results

    @property
    def total_chunks(self) -> int:
        """Số lượng chunks đã index."""
        return self.index.ntotal if self.index else 0


# Singleton instance
vector_store = VectorStore()
