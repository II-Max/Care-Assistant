# 🏗️ Kiến trúc Hệ thống & Công nghệ AI

## 1. Tổng quan kiến trúc

```
┌──────────────────────────────────────────────────────────────────┐
│                        BROWSER                                   │
│  (trang html tĩnh — fetch API cùng domain)                       │
│  index.html → /api/ai/chat                                       │
│  ai-chat.html → /api/ai/chat                                     │
└────────────────────────┬─────────────────────────────────────────┘
                         │ HTTP (JSON)
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                 FASTAPI (ai-service/main.py)                     │
│  Port 8001 — serve static + REST API                             │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    SERVICES LAYER                            │ │
│  │                                                              │ │
│  │  ┌──────────────┐  ┌────────────────┐  ┌────────────────┐   │ │
│  │  │ ChatService  │  │ Emergency      │  │ Rate Limiter   │   │ │
│  │  │ (RAG+LLM)    │  │ Detector       │  │ (SlidingWindow)│   │ │
│  │  │              │  │ (fail-safe     │  │                │   │ │
│  │  │              │  │  rule-based)   │  │                │   │ │
│  │  └───────┬──────┘  └────────────────┘  └────────────────┘   │ │
│  └──────────┼────────────────────────────────────────────────────┘ │
│             │                                                      │
│  ┌──────────┴────────────────────────────────────────────────────┐ │
│  │                     RAG LAYER                                 │ │
│  │                                                               │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐  │ │
│  │  │ Document     │  │ Chunker      │  │ Embedder           │  │ │
│  │  │ Loader       │  │ (Semantic    │  │ (NVIDIA NIM API    │  │ │
│  │  │ (MD + JSON)  │  │  chunking)   │  │  / local fallback) │  │ │
│  │  └──────────────┘  └──────────────┘  └─────────┬──────────┘  │ │
│  │                                                 │             │ │
│  │  ┌──────────────────────────────────────────────┴──────────┐  │ │
│  │  │              VECTOR STORE                               │  │ │
│  │  │  ┌────────┐  ┌──────────────┐  ┌────────────────────┐   │ │ │
│  │  │  │FAISS   │  │ ChromaDB     │  │ BM25 (sparse)      │   │ │ │
│  │  │  │(Phase1)│  │ (Phase 2+)   │  │ (Phase 2+)         │   │ │ │
│  │  │  └────────┘  └──────────────┘  └────────────────────┘   │ │ │
│  │  │  Hybrid: Dense + Sparse → RRF → Cross-encoder reranker  │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    LLM LAYER                                    │  │
│  │  meta/llama-3.1-70b-instruct (NVIDIA NIM API)                  │  │
│  │  → JSON output: {answer, risk_level, handoff_required}         │  │
│  │  → Temperature: 0.1 (deterministic)                            │  │
│  │  → Max tokens: 1024                                            │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

## 2. RAG Pipeline (Chi tiết)

### 2.1 Document Ingestion

```
knowledge/approved/  →  DocumentLoader  →  Chunker  →  Embedder  →  VectorStore
      │                      │                  │           │              │
      │                 - Đọc MD/JSON      - Split theo   - NVIDIA NIM  - FAISS/Chroma
      │                 - Deduplicate        heading       - hoặc local   - Lưu index
      │                 - Bỏ scrap         - Split theo    - 1024 dim     - Query search
      │                   artifacts          paragraph
      │                                      - Merge nhỏ
```

### 2.2 Query Flow

```
User Message
    │
    ▼
[1] Emergency Detector ───┬── keyword match? → EMERGENCY response (1ms)
    │                      │
    │               No match
    ▼                      ▼
[2] Embedding (query) ──→ Vector Search ──→ Top-K chunks
    │                      │
    │               Similarity ≥ 0.60?
    │                      │
    ├── Yes ──────────────→ [3] Build Context → LLM Prompt ──→ Generate
    │                                                              │
    └── No ───────────────→ "Không có thông tin. Liên hệ 19001082" │
                                                                   │
                                                                   ▼
                                                      Response: {answer, sources,
                                                                 risk_level, handoff}
```

### 2.3 System Prompt (Trustworthy AI)

```
QUY TẮC BẮT BUỘC:
1. CHỈ trả lời dựa trên [CONTEXT]. Không bịa, suy đoán.
2. KHÔNG chẩn đoán, tư vấn điều trị, kết luận y khoa.
3. Nếu không có context → khuyên liên hệ tổng đài.
4. Nếu hỏi triệu chứng → khuyên gặp bác sĩ.
5. BẮT BUỘC trả về JSON.
6. Cuối answer phải có disclaimer.
```

## 3. Safety Architecture (3 Layers)

### Layer 1: Emergency Detection (Fail-safe)
- **Cơ chế:** Rule-based regex (keywords)
- **Độ trễ:** < 1ms
- **Recall:** 100% cho keywords cấp cứu
- **Không phụ thuộc LLM:** Phản hồi ngay lập tức

### Layer 2: Retrieval Guardrails
- **Similarity Threshold:** 0.60
- **Không hạ ngưỡng:** Nếu không đủ evidence → từ chối
- **Citation bắt buộc:** Mọi câu trả lời phải có source

### Layer 3: Generation Guardrails
- **System Prompt:** Cấm chẩn đoán, tư vấn y khoa
- **JSON Validation:** Parse output, kiểm tra risk_level
- **Disclaimer:** Ép cứng vào mọi response
- **Rate Limit:** 10 requests/phút/IP

## 4. Công nghệ Chi tiết

| Component | Phase 1 | Phase 2+ |
|-----------|---------|----------|
| **LLM** | meta/llama-3.1-70b-instruct (NVIDIA NIM) | meta/llama-3.1-70b-instruct |
| **Embedding** | nv-embedqa-e5-v5 (NVIDIA NIM) / sentence-transformers | nv-embedqa-e5-v5 + local cache |
| **Vector Store** | FAISS IndexFlatIP (in-memory) | ChromaDB (persistent) |
| **Hybrid Search** | — | BM25 + Dense → RRF → reranker |
| **Reranker** | — | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| **Python** | 3.10+ | 3.10+ |
| **Database** | In-memory | ChromaDB + SQLite (audit) |
| **Monitoring** | print() logs | OpenTelemetry + Prometheus |

## 5. API Endpoints

### POST /api/ai/chat
```json
// Request
{
  "message": "Bệnh viện có khám BHYT không?",
  "conversation_id": null
}

// Response (success)
{
  "reply": "Bệnh viện có nhận khám BHYT...",
  "sources": [{"title": "Dịch vụ Khám & Chữa bệnh", "url": "..."}],
  "is_emergency": false,
  "confidence": 0.87,
  "risk_level": "LOW",
  "handoff_required": false
}

// Response (emergency)
{
  "reply": "🚨 CẢNH BÁO CẤP CỨU...",
  "sources": [],
  "is_emergency": true,
  "confidence": 1.0,
  "risk_level": "HIGH",
  "handoff_required": true
}
```

### GET /api/ai/health
```json
{
  "status": "healthy",
  "documents_loaded": 5,
  "chunks_indexed": 42,
  "model": "meta/llama-3.1-70b-instruct",
  "embedding_model": "nvidia/nv-embedqa-e5-v5"
}
```

## 6. File Structure

```
/
├── ai-service/              # 🚀 Backend chính
│   ├── main.py             # FastAPI entry point
│   ├── config.py           # Settings
│   ├── requirements.txt    # Python dependencies
│   ├── models/
│   │   └── schemas.py      # Pydantic models
│   ├── rag/
│   │   ├── document_loader.py
│   │   ├── chunker.py
│   │   ├── embedder.py
│   │   ├── vector_store.py
│   │   └── retriever.py
│   └── services/
│       ├── emergency_detector.py
│       ├── chat_service.py
│       └── rate_limiter.py
├── frontend/               # 🎨 Giao diện
│   ├── index.html          # Trang chủ
│   ├── ai-chat.html        # Chat AI full page
│   ├── departments.html    # Chuyên khoa
│   ├── contact.html        # Liên hệ
│   ├── about.html          # Giới thiệu
│   ├── css/hospital-design.css
│   └── js/
│       ├── app.js          # Shared utilities
│       └── chat.js         # Chat widget logic
├── knowledge/
│   └── approved/           # 📚 Knowledge Base chính thức
│       ├── gioi-thieu-benh-vien.md
│       ├── dich-vu-kham-chua-benh.md
│       └── lien-he-dat-lich.md
├── Data/                   # 📂 Raw data (lưu giữ)
├── tests/                  # 🧪 Unit tests
├── plans/                  # 📋 Kế hoạch phát triển
│   ├── roadmap.md
│   └── phase2-progress.md
├── start.ps1               # 🚀 Khởi động
├── README.md
└── .gitignore
```
