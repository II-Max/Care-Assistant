"""
Vector Store — ChromaDB persistent vector storage.

Persistent: luu index xuong disk (chroma_db/), khong rebuild moi lan restart.
Fallback ve FAISS in-memory neu ChromaDB khong available.
"""

import logging
from pathlib import Path
from dataclasses import dataclass

import numpy as np

from rag.chunker import Chunk
from rag.embedder import embedder

logger = logging.getLogger("vector_store")

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    chromadb = None


CHROMA_DB_DIR = Path(__file__).resolve().parent.parent.parent / "chroma_db"
COLLECTION_NAME = "hospital_knowledge"


@dataclass
class SearchResult:
    """Ket qua tim kiem tu vector store."""
    chunk: Chunk
    score: float
    rank: int


class VectorStore:
    """Vector store persistent voi ChromaDB. Fallback ve FAISS in-memory."""

    def __init__(self):
        self._collection = None
        self._client = None
        self._fallback_index = None
        self._fallback_chunks: list[Chunk] = []
        self._use_chroma = False
        self.is_initialized = False

    def build_index(self, chunks: list[Chunk]):
        if not chunks:
            logger.warning("Khong co chunks de index")
            return

        if CHROMA_AVAILABLE:
            self._build_chroma(chunks)
        else:
            self._build_faiss(chunks)

    def _build_chroma(self, chunks: list[Chunk]):
        CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)

        try:
            self._client = chromadb.PersistentClient(
                path=str(CHROMA_DB_DIR),
                settings=ChromaSettings(anonymized_telemetry=False)
            )

            try:
                self._client.delete_collection(COLLECTION_NAME)
            except Exception:
                pass

            self._collection = self._client.create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )

            texts = [chunk.embedding_text for chunk in chunks]
            logger.info(f"Dang tao embeddings cho {len(chunks)} chunks...")
            embeddings = embedder.embed_texts(texts)

            if embeddings.size == 0:
                logger.error("Embedding failed — khong co vectors")
                return

            ids = [f"chunk_{i}" for i in range(len(chunks))]
            metadatas = []
            documents = []

            for chunk in chunks:
                documents.append(chunk.text)
                metadatas.append({
                    "title": chunk.title,
                    "source_url": chunk.source_url,
                    "source_file": chunk.source_file,
                    "chunk_index": chunk.chunk_index,
                    "section_header": chunk.section_header,
                })

            self._collection.add(
                ids=ids,
                embeddings=embeddings.tolist(),
                metadatas=metadatas,
                documents=documents
            )

            self._use_chroma = True
            self.is_initialized = True
            logger.info(f"ChromaDB index built: {len(chunks)} vectors, dim={embeddings.shape[1]}")

        except Exception as e:
            logger.error(f"ChromaDB build failed: {e}")
            logger.info("Falling back to FAISS in-memory...")
            self._build_faiss(chunks)

    def _build_faiss(self, chunks: list[Chunk]):
        import faiss
        self._fallback_chunks = chunks
        texts = [chunk.embedding_text for chunk in chunks]
        logger.info(f"Dang tao embeddings cho {len(chunks)} chunks (FAISS fallback)...")
        embeddings = embedder.embed_texts(texts)

        if embeddings.size == 0:
            logger.error("Embedding failed")
            return

        faiss.normalize_L2(embeddings)
        dimension = embeddings.shape[1]
        self._fallback_index = faiss.IndexFlatIP(dimension)
        self._fallback_index.add(embeddings)
        self._use_chroma = False
        self.is_initialized = True
        logger.info(f"FAISS index built: {self._fallback_index.ntotal} vectors, dim={dimension}")

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        if not self.is_initialized:
            logger.warning("Vector store chua initialized")
            return []

        if self._use_chroma:
            return self._search_chroma(query, top_k)
        else:
            return self._search_faiss(query, top_k)

    def _search_chroma(self, query: str, top_k: int) -> list[SearchResult]:
        if not self._collection:
            return []

        query_embedding = embedder.embed_query(query)
        results = self._collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        if not results["ids"][0]:
            return []

        search_results = []
        for rank, (doc_id, distance, metadata, doc_text) in enumerate(
            zip(results["ids"][0], results["distances"][0],
                results["metadatas"][0], results["documents"][0])
        ):
            score = max(0.0, 1.0 - distance / 2.0)
            chunk = Chunk(
                text=doc_text,
                title=metadata.get("title", ""),
                source_url=metadata.get("source_url", ""),
                source_file=metadata.get("source_file", ""),
                chunk_index=metadata.get("chunk_index", 0),
                section_header=metadata.get("section_header", ""),
            )
            search_results.append(SearchResult(chunk=chunk, score=score, rank=rank))

        return search_results

    def _search_faiss(self, query: str, top_k: int) -> list[SearchResult]:
        import faiss
        if self._fallback_index is None:
            return []

        query_vector = embedder.embed_query(query)
        query_vector = query_vector.reshape(1, -1).astype(np.float32)
        faiss.normalize_L2(query_vector)

        top_k = min(top_k, len(self._fallback_chunks))
        scores, indices = self._fallback_index.search(query_vector, top_k)

        results = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < 0 or idx >= len(self._fallback_chunks):
                continue
            results.append(SearchResult(chunk=self._fallback_chunks[idx], score=float(score), rank=rank))

        return results

    @property
    def total_chunks(self) -> int:
        if self._use_chroma and self._collection:
            return self._collection.count()
        elif self._fallback_index is not None:
            return self._fallback_index.ntotal
        return 0

    def get_info(self) -> dict:
        return {
            "type": "chromadb" if self._use_chroma else "faiss_in_memory",
            "total_chunks": self.total_chunks,
            "initialized": self.is_initialized,
            "persistent_path": str(CHROMA_DB_DIR) if self._use_chroma else None,
            "collection": COLLECTION_NAME if self._use_chroma else None
        }


# Singleton instance
vector_store = VectorStore()
