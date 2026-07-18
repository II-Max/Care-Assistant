# 🏥 AI Customer Care Assistant — Bệnh viện Tim Hà Nội
## Implementation Plan (24h Hackathon MVP)

---

## Bối cảnh

Xây dựng toàn bộ hệ thống Trợ lý AI Chăm sóc Khách hàng cho Bệnh viện Tim Hà Nội trong 24h. Hệ thống gồm 3 components: **Frontend Website**, **Flask Backend**, và **FastAPI AI Service (RAG)**.

### Dữ liệu sẵn có

Knowledge Base trong thư mục `Data/` gồm 12 files:
- 1 file JSON tổng hợp (`tat_ca_du_lieu_tong_hop.json` — 38KB, 11 bài viết)
- 11 file Markdown riêng lẻ (trong đó 5 file có nội dung, 6 file chỉ có tiêu đề)

**Nội dung cover:** Giới thiệu BV, Khoa Khám bệnh tự nguyện, Khoa dược, Hướng dẫn đặt lịch khám, Khám sức khỏe doanh nghiệp

**Thông tin liên hệ thực tế:**
- Hotline: `19001082`
- CSKH: `0837091082`, `0836761082`
- Email: `cskh@timhanoi.vn`
- Cơ sở 1: Số 92 Trần Hưng Đạo, Cửa Nam, Hà Nội
- Cơ sở 2: Số 695 Lạc Long Quân, Tây Hồ, Hà Nội
- Website đặt khám: `https://benhvientimhanoi.vn/he-thong/hen-kham/index.html`

---

## User Review Required

> [!IMPORTANT]
> **LLM Choice — NVIDIA NIM API**: Bạn đã confirm có NVIDIA NIM API key. Tôi sẽ dùng:
> - **LLM:** `meta/llama-3.1-70b-instruct` qua NVIDIA NIM API cho chat
> - **Embedding:** `nvidia/nv-embedqa-e5-v5` (hoặc `snowflake/arctic-embed-l`) qua NVIDIA NIM API cho vector embeddings
> 
> Nếu embedding model qua NVIDIA NIM không khả dụng hoặc bạn muốn dùng embedding local miễn phí, tôi sẽ fallback sang `sentence-transformers/all-MiniLM-L6-v2` (chạy local, nhẹ, hỗ trợ tốt tiếng Việt qua cross-lingual).

> [!WARNING]
> **Scope Cut cho 24h**: Để ship được trong 24h, tôi sẽ **cắt bớt** các tính năng sau so với `system_architecture.md`:
> - ❌ Firebase Auth & RTDB (thay bằng in-memory/JSON — demo không cần real DB)
> - ❌ Hệ thống đặt lịch hẹn thực (chỉ redirect đến website BV thật)
> - ❌ Docker Compose (chạy local cho demo)
> - ❌ ASR/TTS (bonus, implement nếu còn thời gian)
> - ❌ Role-based auth (patient/doctor/admin)
> - ✅ **Giữ nguyên toàn bộ:** RAG pipeline, Emergency Detection, Trustworthy AI guardrails, Chat UI đẹp

## Open Questions

> [!IMPORTANT]
> 1. **NVIDIA NIM API key** — bạn sẽ cung cấp key ở bước setup `.env`. Hãy xác nhận format key (thường là `nvapi-xxxx`)?
> 2. **Model embedding** — Bạn muốn dùng NVIDIA NIM embedding API hay chạy embedding local (miễn phí, không cần API)?
> 3. **Scope validation** — Bạn đồng ý với phần scope cut ở trên? Hay có tính năng nào PHẢI có cho demo?

---

## Proposed Changes

### Kiến trúc MVP 24h

```
Care-Assistant/
├── Data/                          # [GIỮ NGUYÊN] Knowledge Base hiện có
│
├── backend/                       # Flask Backend API
│   ├── app.py                     # Flask entry point
│   ├── config.py                  # Settings từ .env
│   └── requirements.txt           # Flask dependencies
│
├── ai-service/                    # FastAPI AI Service (RAG)
│   ├── main.py                    # FastAPI entry point
│   ├── config.py                  # AI settings
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── document_loader.py     # Load & parse MD + JSON
│   │   ├── chunker.py             # Semantic chunking
│   │   ├── embedder.py            # Embedding (NVIDIA NIM / local)
│   │   ├── vector_store.py        # FAISS vector store
│   │   └── retriever.py           # Similarity search
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chat_service.py        # RAG chat pipeline
│   │   └── emergency_detector.py  # Emergency keyword + LLM detection
│   ├── models/
│   │   └── schemas.py             # Pydantic models
│   └── requirements.txt           # FastAPI + FAISS deps
│
├── frontend/                      # Static website
│   ├── index.html                 # Trang chủ BV
│   ├── ai-chat.html               # Chat với AI
│   ├── departments.html           # Danh sách khoa
│   ├── contact.html               # Liên hệ
│   ├── about.html                 # Giới thiệu BV
│   ├── css/
│   │   └── hospital-design.css    # Design system y tế
│   └── js/
│       ├── app.js                 # Shared utilities
│       └── chat.js                # Chat widget logic
│
├── .env.example                   # Template biến môi trường
├── README.md                      # [CẬP NHẬT] Hướng dẫn chạy
└── start.ps1                      # Script khởi động cả 2 services
```

---

### Component 1: AI Service (FastAPI + RAG) — ĐỘ ƯU TIÊN CAO NHẤT

> Đây là **trái tim** của sản phẩm, cần build đầu tiên.

#### [NEW] `ai-service/main.py`
- FastAPI app chạy port `8001`
- Startup event: load documents → chunk → embed → index FAISS
- Endpoints: `POST /api/ai/chat`, `GET /api/ai/health`
- CORS cho frontend

#### [NEW] `ai-service/config.py`
- Đọc `.env`: `NVIDIA_API_KEY`, `NVIDIA_MODEL`, `EMBEDDING_MODEL`
- Config chunk size, overlap, top-K, similarity threshold

#### [NEW] `ai-service/rag/document_loader.py`
- Load tất cả file `.md` và `.json` từ `Data/`
- Parse JSON array → extract `title` + `content` arrays
- Parse Markdown → extract sections
- Output: list of `Document(title, content, source_url)`

#### [NEW] `ai-service/rag/chunker.py`
- Semantic chunking: split by heading/paragraph
- Chunk size: ~500 tokens, overlap ~50 tokens
- Mỗi chunk giữ metadata: `source_title`, `source_url`, `chunk_index`

#### [NEW] `ai-service/rag/embedder.py`
- Primary: NVIDIA NIM Embedding API (`nvidia/nv-embedqa-e5-v5`)
- Fallback: `sentence-transformers` local model
- Interface: `embed_texts(texts: List[str]) → List[List[float]]`

#### [NEW] `ai-service/rag/vector_store.py`
- FAISS flat index (đơn giản, đủ cho ~100 chunks)
- Methods: `add_documents()`, `search(query, top_k=5)`
- Serialize/deserialize index cho startup nhanh

#### [NEW] `ai-service/rag/retriever.py`
- Pipeline: query → embed → FAISS search → filter by threshold (0.65)
- Return top-K chunks kèm similarity scores

#### [NEW] `ai-service/services/emergency_detector.py`
- **Layer 1 (Rule-based):** Keyword matching — danh sách ~30 từ khóa cấp cứu tim mạch tiếng Việt
- **Layer 2 (LLM):** Nếu Layer 1 trigger, confirm bằng LLM classification
- Response cấp cứu hard-coded: số 115, địa chỉ Khoa Cấp cứu BV Tim HN

#### [NEW] `ai-service/services/chat_service.py`
- Full RAG pipeline:
  1. Emergency check → nếu emergency → return emergency response
  2. Embed query → retrieve top-K
  3. Nếu max similarity < threshold → return "ngoài phạm vi"
  4. Build augmented prompt (system prompt + context + query)
  5. Call NVIDIA NIM LLM
  6. Append disclaimer + source citations
- System prompt tuân thủ Trustworthy AI guidelines

#### [NEW] `ai-service/models/schemas.py`
- `ChatRequest(message: str, conversation_id: Optional[str])`
- `ChatResponse(reply: str, sources: List[Source], is_emergency: bool)`
- `Source(title: str, url: str)`

#### [NEW] `ai-service/requirements.txt`
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
faiss-cpu>=1.7.4
numpy>=1.24.0
openai>=1.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

> **Note:** Dùng `openai` SDK với custom `base_url` để gọi NVIDIA NIM API (compatible OpenAI format)

---

### Component 2: Frontend Website — ĐỘ ƯU TIÊN CAO

#### [NEW] `frontend/css/hospital-design.css`
- Design system y tế chuyên nghiệp
- Color: Primary `#0077B6`, Secondary `#00B4D8`, Accent `#90E0EF`
- Font: Inter (Google Fonts)
- Mobile-first responsive
- Chat widget floating button + panel
- Smooth animations, glassmorphism cards
- Dark mode KHÔNG bật (y tế → sáng, sạch, tin cậy)

#### [NEW] `frontend/index.html`
- Hero banner với slogan "Vì Một Trái Tim Khỏe"
- Section: Giới thiệu, 5 lĩnh vực chuyên khoa, Thống kê BV
- CTA: Đặt lịch khám (link website BV thật), Chat AI
- Floating AI chat widget (mọi trang)
- Footer: 2 cơ sở, hotline, email

#### [NEW] `frontend/ai-chat.html`
- Trang chat AI toàn màn hình
- UI kiểu messenger: bubbles, typing indicator, timestamps
- Gợi ý câu hỏi nhanh (quick replies)
- Emergency alert banner khi phát hiện cấp cứu
- Disclaimer y tế ở header

#### [NEW] `frontend/departments.html`
- Grid cards 5 chuyên khoa: Nội, Ngoại, Nhi, Can thiệp, Chuyển hóa
- Mỗi card: icon, mô tả, link chi tiết

#### [NEW] `frontend/contact.html`
- Thông tin 2 cơ sở (địa chỉ, bản đồ Google Maps embed)
- Hotline click-to-call (`tel:19001082`)
- Email, website
- Nút Zalo placeholder

#### [NEW] `frontend/about.html`
- Lịch sử BV, sứ mệnh, cam kết
- Cơ cấu tổ chức, nhân lực
- Trang thiết bị, thành tựu

#### [NEW] `frontend/js/chat.js`
- Chat widget logic: open/close, send message, display response
- Gọi `POST /api/ai/chat` tới AI service
- Emergency alert rendering
- Quick reply suggestions
- Typing indicator animation
- Local conversation history (sessionStorage)

#### [NEW] `frontend/js/app.js`
- Shared utilities: API base URL, navbar injection
- Chat widget initialization (mọi trang)
- Mobile menu toggle

---

### Component 3: Flask Backend (Proxy + Static) — ĐỘ ƯU TIÊN TRUNG BÌNH

#### [NEW] `backend/app.py`
- Flask app chạy port `5000`
- Serve static files từ `frontend/`
- Proxy endpoint `/api/ai/chat` → forward tới FastAPI `localhost:8001`
- Health check `/api/health`
- CORS configuration

#### [NEW] `backend/config.py`
- Đọc `.env` settings
- AI service URL, allowed origins

#### [NEW] `backend/requirements.txt`
```
flask>=3.0.0
flask-cors>=4.0.0
requests>=2.31.0
python-dotenv>=1.0.0
```

---

### Config & DevOps

#### [NEW] `.env.example`
```env
# NVIDIA NIM API
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxx
NVIDIA_MODEL=meta/llama-3.1-70b-instruct
NVIDIA_EMBED_MODEL=nvidia/nv-embedqa-e5-v5

# AI Service
AI_SERVICE_PORT=8001
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K=5
SIMILARITY_THRESHOLD=0.65

# Flask Backend
FLASK_PORT=5000
AI_SERVICE_URL=http://localhost:8001
```

#### [NEW] `start.ps1`
- PowerShell script khởi động AI service + Flask backend song song

---

## Thứ tự triển khai (Timeline 24h)

| Phase | Thời gian | Tasks | Deliverable |
|-------|-----------|-------|-------------|
| **1** | 0h–6h | AI Service: RAG pipeline + Emergency Detection | API `/api/ai/chat` hoạt động |
| **2** | 6h–12h | Frontend: Design system + Chat UI + Trang chủ | Website đẹp + Chat widget |
| **3** | 12h–16h | Frontend: Các trang phụ + Flask proxy | Website hoàn chỉnh |
| **4** | 16h–20h | Integration test + Polish | E2E working demo |
| **5** | 20h–24h | Bug fixes + Defense strategy + Documentation | Ship! |

---

## Verification Plan

### Automated Tests
- AI Service health check: `GET http://localhost:8001/api/ai/health`
- RAG test queries:
  - "Đặt lịch khám như thế nào?" → trả lời từ knowledge base
  - "Giá khám bao nhiêu?" → trả lời hoặc redirect hotline
  - "Tôi đau ngực dữ dội" → EMERGENCY response
  - "Cho hỏi về bệnh dạ dày" → "ngoài phạm vi" + redirect hotline

### Manual Verification
- [ ] Chat widget hoạt động trên mobile
- [ ] Emergency detection kích hoạt đúng
- [ ] Không có hallucination (câu trả lời grounded từ KB)
- [ ] Nút gọi điện hoạt động (`tel:` protocol)
- [ ] Trang web responsive, design chuyên nghiệp
- [ ] AI từ chối câu hỏi ngoài phạm vi đúng cách
