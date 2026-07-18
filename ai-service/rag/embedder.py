"""
Embedder — Tạo vector embeddings cho text.

Primary: NVIDIA NIM Embedding API (nvidia/nv-embedqa-e5-v5)
Fallback: sentence-transformers local model (nếu API fail)
"""

import numpy as np
from typing import Optional
from openai import OpenAI

from config import settings


class Embedder:
    """Tạo embeddings cho text sử dụng NVIDIA NIM API."""

    def __init__(self):
        self.client: Optional[OpenAI] = None
        self.model = settings.NVIDIA_EMBED_MODEL
        self.dimension: int = 0
        self._fallback_model = None

    def initialize(self):
        """Khởi tạo embedding client."""
        # Thử NVIDIA API nếu có key
        if settings.NVIDIA_API_KEY:
            try:
                self.client = OpenAI(
                    api_key=settings.NVIDIA_API_KEY,
                    base_url=settings.NVIDIA_BASE_URL
                )
                test_result = self._embed_nvidia(["test"])
                self.dimension = len(test_result[0])
                print(f"✅ NVIDIA Embedding ready: model={self.model}, dim={self.dimension}")
                return
            except Exception as e:
                print(f"⚠️  NVIDIA Embedding failed: {e}")
                self.client = None

        # Fallback: sentence-transformers
        print("🔄 Falling back to local sentence-transformers...")
        self._init_fallback()

    def _init_fallback(self):
        """Khởi tạo fallback embedding model local."""
        try:
            from sentence_transformers import SentenceTransformer
            self._fallback_model = SentenceTransformer("all-MiniLM-L6-v2")
            self.dimension = 384  # all-MiniLM-L6-v2 dimension
            print(f"✅ Fallback Embedding ready: all-MiniLM-L6-v2, dim={self.dimension}")
        except ImportError:
            print("❌ sentence-transformers chưa cài. Chạy: pip install sentence-transformers")
            raise

    def embed_texts(
        self,
        texts: list[str],
        input_type: str = "passage"
    ) -> np.ndarray:
        """Tạo embeddings cho danh sách texts.

        Args:
            texts: Danh sách strings cần embed

        Returns:
            numpy array shape (len(texts), dimension)
        """
        if not texts:
            return np.array([])

        if self._fallback_model:
            return self._embed_local(texts)
        else:
            return self._embed_nvidia(texts, input_type=input_type)

    def embed_query(self, query: str) -> np.ndarray:
        """Tạo embedding cho một query duy nhất."""
        result = self.embed_texts([query], input_type="query")
        return result[0]

    def _embed_nvidia(
        self,
        texts: list[str],
        input_type: str = "passage"
    ) -> np.ndarray:
        """Embed qua NVIDIA NIM API.

        NVIDIA NIM API có giới hạn batch size, nên chia batch nếu cần.
        """
        all_embeddings = []
        batch_size = 50  # NVIDIA NIM batch limit

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            # Truncate texts quá dài
            batch = [t[:8000] if len(t) > 8000 else t for t in batch]

            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                    encoding_format="float",
                    extra_body={"input_type": input_type, "truncate": "END"}
                )
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
            except Exception as e:
                print(f"⚠️  NVIDIA embed batch failed: {e}")
                # Nếu NVIDIA fail, switch sang fallback
                if not self._fallback_model:
                    self._init_fallback()
                return self._embed_local(texts)

        return np.array(all_embeddings, dtype=np.float32)

    def _embed_local(self, texts: list[str]) -> np.ndarray:
        """Embed local với sentence-transformers."""
        embeddings = self._fallback_model.encode(
            texts,
            show_progress_bar=False,
            normalize_embeddings=True
        )
        return np.array(embeddings, dtype=np.float32)


# Singleton instance
embedder = Embedder()
