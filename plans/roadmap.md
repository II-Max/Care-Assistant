# 🗺️ Lộ trình Phát triển — AI Customer Care Assistant
## Bệnh viện Tim Hà Nội

> **Trạng thái:** `Phase 1 ✅ HOÀN THÀNH` → `Phase 2 🔄 ĐANG THỰC HIỆN`
> **Cập nhật lần cuối:** 18/07/2026

---

## 📊 Tổng quan tiến độ

| Phase | Mô tả | Trạng thái | Tiến độ |
|-------|-------|-----------|---------|
| **Phase 1** | Foundation & Safety Release | ✅ **Hoàn thành** | 100% |
| **Phase 2** | Grounded RAG & Operability | 🔄 **Đang thực hiện** | 25% |
| **Phase 3** | Booking & Hospital Integration | ⏳ **Chưa bắt đầu** | 0% |
| **Phase 4** | Production Readiness | ⏳ **Chưa bắt đầu** | 0% |

---

## ✅ Phase 1 — Foundation & Safety (HOÀN THÀNH)

**Mục tiêu:** Xây dựng nền tảng an toàn cho AI Customer Care Assistant

### Công việc đã hoàn thành

| STT | Công việc | File / Module | Trạng thái |
|-----|-----------|---------------|------------|
| 1 | FastAPI làm cổng web và API duy nhất | `ai-service/main.py` | ✅ |
| 2 | Serve static frontend từ FastAPI | `ai-service/main.py` | ✅ |
| 3 | Emergency detection fail-safe (rule-based) | `ai-service/services/emergency_detector.py` | ✅ |
| 4 | CORS allowlist (không wildcard) | `ai-service/main.py` | ✅ |
| 5 | Rate limiter in-memory | `ai-service/services/rate_limiter.py` | ✅ |
| 6 | Security headers (X-Content-Type-Options, X-Frame-Options, etc.) | `ai-service/main.py` | ✅ |
| 7 | Document loader loại bỏ scrap artifacts | `ai-service/rag/document_loader.py` | ✅ |
| 8 | Deduplicate nội dung khi load | `ai-service/rag/document_loader.py` | ✅ |
| 9 | Phân biệt embedding passage/query | `ai-service/rag/embedder.py` | ✅ |
| 10 | Không hạ ngưỡng retrieval — từ chối khi thiếu evidence | `ai-service/rag/retriever.py` | ✅ |
| 11 | Loại bỏ URL AI hardcode ở frontend | `frontend/js/app.js` | ✅ |
| 12 | Giới hạn link chat tới domain chính thức | `frontend/js/chat.js` → `safeOfficialUrl()` | ✅ |
| 13 | Ép LLM trả JSON có answer, risk_level, handoff_required | `ai-service/services/chat_service.py` | ✅ |
| 14 | .gitignore, .env.example | Root | ✅ |
| 15 | Unit tests cho safety/retrieval | `tests/test_phase1_safety.py`, `tests/test_safety.py` | ✅ |
| 16 | Frontend: Trang chủ, Chat AI, Chuyên khoa, Liên hệ, Giới thiệu | `frontend/*.html` | ✅ |
| 17 | Design system y tế (hospital-design.css) | `frontend/css/hospital-design.css` | ✅ |
| 18 | Chat widget floating + full page | `frontend/js/chat.js` | ✅ |
| 19 | `start.ps1` script khởi động | Root | ✅ |
| 20 | Knowledge Base cô đọng thành 3 file | `knowledge/approved/` | ✅ |

### Kiểm tra Phase 1

```bash
# Kiểm tra emergency detection
curl -X POST http://localhost:8001/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tôi đau ngực dữ dội"}'
# → Phải trả về EMERGENCY response

# Kiểm tra health check
curl http://localhost:8001/api/ai/health
# → {"status": "healthy", ...}

# Kiểm tra CORS
curl -I -X OPTIONS http://localhost:8001/api/ai/chat \
  -H "Origin: http://localhost:8001"
# → Phải có Access-Control-Allow-Origin
```

---

## 🔄 Phase 2 — Grounded RAG & Operability (ĐANG THỰC HIỆN)

**Mục tiêu:** Nâng cấp RAG pipeline với hybrid search, citation validation, monitoring, và persistent storage

### Công việc

| STT | Công việc | File / Module | Trạng thái |
|-----|-----------|---------------|------------|
| **2.1** | **Knowledge Management** | | |
| 2.1.1 | Tạo `knowledge/approved/` với content manifest | `knowledge/approved/` | ✅ |
| 2.1.2 | Thêm metadata: owner, approved_at, expires_at | `knowledge/approved/manifest.json` | 🔄 |
| 2.1.3 | Cô đọng Data/ → 3 file knowledge chính thức | `knowledge/approved/` | ✅ |
| **2.2** | **Persistent Vector Store** | | |
| 2.2.1 | Thay FAISS in-memory bằng ChromaDB persistent | `ai-service/rag/vector_store.py` | ⏳ |
| 2.2.2 | Lưu index xuống disk, không rebuild mỗi lần restart | `ai-service/rag/vector_store.py` | ⏳ |
| **2.3** | **Hybrid Retrieval** | | |
| 2.3.1 | Thêm BM25 sparse retrieval | `ai-service/rag/hybrid_retriever.py` | ⏳ |
| 2.3.2 | RRF (Reciprocal Rank Fusion) kết hợp dense + sparse | `ai-service/rag/hybrid_retriever.py` | ⏳ |
| 2.3.3 | Cross-encoder reranker (tăng precision) | `ai-service/rag/reranker.py` | ⏳ |
| **2.4** | **Citation Validation** | | |
| 2.4.1 | Xác thực citation trước khi trả frontend | `ai-service/services/chat_service.py` | ⏳ |
| 2.4.2 | Đảm bảo 100% câu trả lời có citation hoặc fallback | `ai-service/services/chat_service.py` | ⏳ |
| **2.5** | **Feedback & Monitoring** | | |
| 2.5.1 | Feedback workflow (user đánh giá câu trả lời) | `ai-service/models/schemas.py` | ⏳ |
| 2.5.2 | Audit log ẩn danh | `ai-service/services/audit_service.py` | ⏳ |
| 2.5.3 | OpenTelemetry tracing | `ai-service/services/telemetry.py` | ⏳ |
| 2.5.4 | Prometheus metrics + Grafana dashboard | `ai-service/metrics/` | ⏳ |
| **2.6** | **Evaluation** | | |
| 2.6.1 | Tạo bộ 150 câu hỏi tiếng Việt | `tests/test_questions.json` | ⏳ |
| 2.6.2 | CI pipeline đo Groundedness, Recall@20 | `.github/workflows/` | ⏳ |
| **2.7** | **Document Expiry** | | |
| 2.7.1 | Tài liệu hết hiệu lực không được retrieval | `ai-service/rag/document_loader.py` | ⏳ |
| 2.7.2 | Content review workflow | `knowledge/approved/manifest.json` | ⏳ |

### Kiểm tra Phase 2

```bash
# Kiểm tra hybrid search (khi hoàn thành)
curl -X POST http://localhost:8001/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "BHYT trái tuyến có được chi trả không?"}'
# → Phải có sources với link chính thống

# Kiểm tra citation
# → Mọi response phải có ít nhất 1 source
```

---

## ⏳ Phase 3 — Booking & Hospital Integration (CHƯA BẮT ĐẦU)

**Mục tiêu:** Kết nối với hệ thống đặt lịch bệnh viện, Zalo, SMS

| Công việc | Mô tả |
|-----------|-------|
| PostgreSQL cho appointments, schedules, users | Database layer |
| Booking transaction với idempotency key | Chống trùng slot |
| Redis + worker cho notification, indexing | Async processing |
| HIS Adapter (Hệ thống thông tin BV) | Integration |
| Zalo/SMS/Email Adapter | Notification |
| Human handoff (chuyển sang nhân viên) | Escalation |
| OIDC/Keycloak hoặc Firebase Auth | Authentication |
| RBAC: patient, doctor, admin | Role-based access |

---

## ⏳ Phase 4 — Production Readiness (CHƯA BẮT ĐẦU)

**Mục tiêu:** Docker hóa, CI/CD, security audit

| Công việc | Mô tả |
|-----------|-------|
| Docker Compose production | Multi-service deployment |
| CI/CD pipeline (GitHub Actions) | Lint, test, build, deploy |
| TLS, WAF, rate limit tại gateway | Security |
| Backup/restore có kiểm thử | Data safety |
| Secret rotation | Operational security |
| Incident runbook | Playbook cho sự cố |
| PII assessment (dữ liệu cá nhân) | Privacy compliance |
| Retention policy | Data lifecycle |
| Penetration testing | Security audit |
| SLO, alerting, on-call | Observability |

---

## 📋 Architecture Overview (cập nhật)

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND                                │
│  (FastAPI serves static — HTML/CSS/JS)                       │
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐   │
│  │ Trang chủ│ │ Chat AI  │ │Chuyên khoa│ │ Liên hệ       │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬────────┘   │
│       │             │            │               │            │
│       └─────────────┼────────────┼───────────────┘            │
│                     │            │                             │
│         Fetch API   │    Cùng domain                          │
└─────────────────────┼────────────┼─────────────────────────────┘
                      │            │
                      ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│              FASTAPI SERVER (Port 8001)                       │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────────────────────┐  │
│  │ API Endpoints    │  │ Static File Serving              │  │
│  │                  │  │                                  │  │
│  │ POST /api/ai/chat│  │ /index.html, /ai-chat.html      │  │
│  │ GET  /api/ai/health│ │ /departments.html, /contact.html │  │
│  └────────┬─────────┘  └──────────────────────────────────┘  │
│           │                                                   │
│  ┌────────┴────────────────────────────────────────────────┐  │
│  │                    SERVICES LAYER                        │  │
│  │  ┌─────────────┐ ┌──────────────┐ ┌──────────────────┐  │  │
│  │  │ChatService  │ │Emergency     │ │RateLimiter       │  │  │
│  │  │(RAG+LLM)    │ │Detector      │ │(Sliding Window)  │  │  │
│  │  └──────┬──────┘ └──────────────┘ └──────────────────┘  │  │
│  └─────────┼────────────────────────────────────────────────┘  │
│            │                                                   │
│  ┌─────────┴────────────────────────────────────────────────┐  │
│  │                    RAG LAYER (Phase 2)                    │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │  │
│  │  │ Document     │  │ Chunker      │  │ Embedder       │  │  │
│  │  │ Loader       │  │ (Semantic)   │  │ (NVIDIA/vLLM)  │  │  │
│  │  └──────────────┘  └──────────────┘  └───────┬────────┘  │  │
│  │                                               │           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────┴────────┐  │  │
│  │  │ Vector Store │  │ BM25         │  │ Reranker       │  │  │
│  │  │ (ChromaDB)   │  │ (Sparse)     │  │ (Cross-encoder)│  │  │
│  │  └──────────────┘  └──────────────┘  └────────────────┘  │  │
│  │                                                          │  │
│  │  Hybrid Search: Dense + Sparse → RRF → Reranker          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              KNOWLEDGE MANAGEMENT (Phase 2)              │  │
│  │  ┌──────────────────────┐  ┌──────────────────────────┐  │  │
│  │  │ knowledge/approved/  │  │ Manifest (owner, expiry) │  │  │
│  │  │ (3 files chính thức) │  │ + Expiry validation     │  │  │
│  │  └──────────────────────┘  └──────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              MONITORING (Phase 2)                        │  │
│  │  Prometheus → Grafana → OpenTelemetry → Audit Log       │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

---

## 🔧 Công nghệ (Technology Stack)

| Layer | Công nghệ | Phase |
|-------|-----------|-------|
| **Backend** | FastAPI (Python 3.10+) | P1 |
| **Frontend** | Vanilla HTML/CSS/JS | P1 |
| **AI Service** | NVIDIA NIM API (`meta/llama-3.1-70b-instruct`) | P1 |
| **Embedding** | NVIDIA NIM (`nv-embedqa-e5-v5`) / sentence-transformers fallback | P1 |
| **Vector Store** | FAISS (P1) → **ChromaDB** (P2) | P2 |
| **Hybrid Search** | BM25 + Dense → RRF → Cross-encoder reranker | P2 |
| **Database** | In-memory (P1-P2) → **PostgreSQL** (P3) | P3 |
| **Queue** | Redis (P3) | P3 |
| **Monitoring** | Prometheus + Grafana + OpenTelemetry (P2) | P2 |
| **Container** | Docker + Docker Compose | P4 |
| **CI/CD** | GitHub Actions | P4 |

---

> 📝 **Ghi chú:** Các mục trong Phase 2 được ưu tiên theo thứ tự từ trên xuống dưới. Bắt đầu với Knowledge Management và Persistent Vector Store trước.
