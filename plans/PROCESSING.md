# ✅ PROCESSING — Tiến độ dự án AI Customer Care Assistant

> **Dự án:** AI Customer Care Assistant — Bệnh viện Tim Hà Nội
> **Cập nhật:** `18/07/2026` **|** **Tổng tiến độ:** `~65%`
> **Trạng thái:** `Phase 1 ✅` | `Phase 2 ✅` | `Phase 3 🔄` | `Phase 4 ⏳` | `Phase 5 ⏳`

---

## 📊 Tổng quan tiến độ các Phase

```
Phase 1: Foundation & Safety     [████████████████████ 100%] ✅ HOÀN THÀNH
Phase 2: Grounded RAG            [████████████████████ 100%] ✅ HOÀN THÀNH
Phase 3: Booking & Integration   [██████████████░░░░░░  70%] 🔄 ĐANG THỰC HIỆN
Phase 4: Production Readiness    [░░░░░░░░░░░░░░░░░░░░   0%] ⏳ KẾ HOẠCH
Phase 5: Future & Expansion      [░░░░░░░░░░░░░░░░░░░░   0%] ⏳ KẾ HOẠCH
```

---

## 🟢 Phase 1 — Foundation & Safety Release Blockers

> **Trạng thái:** `✅ HOÀN THÀNH 100%`
> **Mục tiêu:** Xây dựng nền tảng an toàn cho AI Customer Care Assistant

### Kiến trúc tổng thể Phase 1

```
┌──────────────────────────────────────────────────────────────────┐
│                        FRONTEND                                  │
│  (FastAPI serves static — HTML/CSS/JS)                            │
│                                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐        │
│  │ Trang chủ│ │ Chat AI  │ │Chuyên khoa│ │ Đặt lịch      │        │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬────────┘        │
│       │             │            │               │                 │
│       └─────────────┼────────────┼───────────────┘                 │
│                     │            │                                  │
│         Fetch API   │    Cùng domain                               │
└─────────────────────┼────────────┼──────────────────────────────────┘
                      │            │
                      ▼            ▼
┌──────────────────────────────────────────────────────────────────┐
│                     FASTAPI SERVER (Port 8001)                     │
│                                                                    │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐  │
│  │ API Endpoints        │  │ Static File Serving              │  │
│  │                      │  │                                  │  │
│  │ POST /api/ai/chat    │  │ /index.html, /ai-chat.html      │  │
│  │ GET  /api/ai/health  │  │ /departments.html, /booking.html│  │
│  └────────┬─────────────┘  └──────────────────────────────────┘  │
│           │                                                       │
│  ┌────────┴────────────────────────────────────────────────────┐  │
│  │                    SERVICES LAYER                            │  │
│  │  ┌─────────────┐ ┌──────────────┐ ┌──────────────────┐     │  │
│  │  │ChatService  │ │Emergency     │ │RateLimiter       │     │  │
│  │  │(RAG + LLM)  │ │Detector      │ │(Sliding Window)  │     │  │
│  │  └──────┬──────┘ └──────────────┘ └──────────────────┘     │  │
│  └─────────┼────────────────────────────────────────────────────┘  │
│            │                                                       │
│  ┌─────────┴────────────────────────────────────────────────────┐  │
│  │                    RAG LAYER                                  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐     │  │
│  │  │ Document     │  │ Chunker      │  │ Embedder       │     │  │
│  │  │ Loader       │  │ (Semantic)   │  │ (NVIDIA NIM)   │     │  │
│  │  └──────────────┘  └──────────────┘  └───────┬────────┘     │  │
│  │                                               │              │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────┴────────┐     │  │
│  │  │ Vector Store │  │ BM25         │  │ Reranker       │     │  │
│  │  │ (ChromaDB)   │  │ (Sparse)     │  │ (Cross-encoder)│     │  │
│  │  └──────────────┘  └──────────────┘  └────────────────┘     │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              KNOWLEDGE MANAGEMENT                             │  │
│  │  ┌──────────────────────┐  ┌──────────────────────────────┐  │  │
│  │  │ knowledge/approved/  │  │ Manifest (owner, expiry)     │  │  │
│  │  │ (3 files chính thức) │  │ + Expiry validation          │  │  │
│  │  └──────────────────────┘  └──────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### Chi tiết công việc

| STT | Công việc | Module / File | Mô tả | Trạng thái |
|:---:|-----------|---------------|-------|:----------:|
| 1.1 | **FastAPI Server** | `ai-service/main.py` | Cổng web và API duy nhất, serve cả static + API | `✅` |
| 1.2 | **Emergency Detection** | `services/emergency_detector.py` | Layer 1 fail-safe: keywords → response ngay, không đợi LLM | `✅` |
| 1.3 | **CORS** | `ai-service/main.py` | Allowlist origins, không wildcard `*` | `✅` |
| 1.4 | **Rate Limiter** | `services/rate_limiter.py` | Sliding window: 10 requests/phút/IP | `✅` |
| 1.5 | **Security Headers** | `ai-service/main.py` middleware | X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Cache-Control | `✅` |
| 1.6 | **Document Loader** | `rag/document_loader.py` | Load từ `knowledge/approved/`, loại bỏ scrap artifacts, dedup | `✅` |
| 1.7 | **Chunker** | `rag/chunker.py` | Semantic chunking với overlap | `✅` |
| 1.8 | **Embedder** | `rag/embedder.py` | NVIDIA NIM embedding, phân biệt passage/query | `✅` |
| 1.9 | **Vector Store** | `rag/vector_store.py` | FAISS → ChromaDB persistent | `✅` |
| 1.10 | **Retriever** | `rag/retriever.py` | Similarity threshold `0.35`, không hạ ngưỡng | `✅` |
| 1.11 | **Chat Service** | `services/chat_service.py` | LLM orchestration, ép JSON output | `✅` |
| 1.12 | **Frontend Pages** | `frontend/*.html` | 6 trang: index, ai-chat, booking, departments, about, contact | `✅` |
| 1.13 | **Design System** | `frontend/css/hospital-design.css` | Mobile-first, WCAG 2.1 AA, responsive | `✅` |
| 1.14 | **Chat JS** | `frontend/js/chat.js` | Chat widget, API calls, `safeOfficialUrl()` | `✅` |
| 1.15 | **Start Script** | `start.ps1` | Khởi động 1 câu lệnh | `✅` |
| 1.16 | **Config** | `ai-service/config.py` | Settings: NVIDIA, DB, Firebase, CORS | `✅` |
| 1.17 | **Unit Tests** | `tests/test_phase1_safety.py` | 5 tests cho safety & retrieval | `✅` |
| 1.18 | **Git & Env** | `.gitignore`, `env.example.txt` | Template môi trường, ignore rules | `✅` |

---

## 🟢 Phase 2 — Grounded RAG & Operability

> **Trạng thái:** `✅ HOÀN THÀNH 100%`
> **Mục tiêu:** Nâng cấp RAG pipeline với hybrid search, citation validation, monitoring

### Chi tiết công việc

| STT | Công việc | Module / File | Mô tả | Trạng thái |
|:---:|-----------|---------------|-------|:----------:|
| 2.1 | **Knowledge Management** | `knowledge/approved/` | 3 files chính thức + manifest.json | `✅` |
| 2.2 | **Content Metadata** | `knowledge/approved/manifest.json` | owner, approved_at, expires_at | `✅` |
| 2.3 | **ChromaDB Persistent** | `rag/vector_store.py` | Lưu index xuống disk, không rebuild mỗi lần | `✅` |
| 2.4 | **BM25 Sparse Retrieval** | `rag/bm25_search.py` | TF-IDF based sparse search | `✅` |
| 2.5 | **Hybrid Retriever** | `rag/hybrid_retriever.py` | Dense + Sparse → RRF | `✅` |
| 2.6 | **Cross-encoder Reranker** | `rag/hybrid_retriever.py` | `ms-marco-MiniLM-L-6-v2` tăng precision | `✅` |
| 2.7 | **Citation Validation** | `services/chat_service.py` | Xác thực citation trước khi trả frontend | `✅` |
| 2.8 | **LLM JSON Output** | `services/chat_service.py` | answer, citations, handoff_required, risk_level | `✅` |
| 2.9 | **Feedback Workflow** | `main.py → POST /api/ai/feedback` | User đánh giá 1–5 sao | `✅` |
| 2.10 | **Audit Log (Firebase)** | `services/firebase/client.py` | Log ẩn danh, hash IP | `✅` |
| 2.11 | **Conversation History** | `main.py → GET /api/ai/conversation/{id}` | Lấy lịch sử hội thoại | `✅` |
| 2.12 | **Document Expiry** | `rag/document_loader.py` | Tài liệu hết hạn không được retrieval | `✅` |

---

## 🟡 Phase 3 — Booking & Hospital Integration

> **Trạng thái:** `🔄 ĐANG THỰC HIỆN (70%)`
> **Mục tiêu:** Kết nối với hệ thống đặt lịch bệnh viện, Firebase, notification

### Kiến trúc Phase 3

```
┌──────────────────────────────────────────────────────────────────┐
│                      FRONTEND                                     │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐   │
│  │ Chat AI        │  │ Booking Form   │  │ Booking History  │   │
│  │ (ai-chat.html) │  │ (booking.html) │  │ (future)         │   │
│  └────────┬───────┘  └───────┬────────┘  └────────┬─────────┘   │
│           │                  │                    │              │
└───────────┼──────────────────┼────────────────────┼──────────────┘
            │                  │                    │
            ▼                  ▼                    ▼
┌──────────────────────────────────────────────────────────────────┐
│                     FASTAPI — API LAYER                            │
│                                                                    │
│  POST /api/ai/chat        POST /api/ai/booking                    │
│  POST /api/ai/handoff     GET  /api/ai/booking/{id}                │
│  POST /api/ai/feedback    POST /api/ai/booking/{id}/cancel         │
│  GET  /api/ai/conversation GET /api/ai/booking/lookup              │
│                            GET  /api/ai/departments                │
└─────────────────────┬──────────────────────────────────────────────┘
                      │
┌─────────────────────┴──────────────────────────────────────────────┐
│                     SERVICES LAYER                                  │
│                                                                    │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐  │
│  │ ChatService      │  │ BookingService   │  │ HandoffService │  │
│  │ (RAG + LLM)      │  │ (CRUD + Validate)│  │ (Ticket-based) │  │
│  └──────────────────┘  └────────┬─────────┘  └───────┬────────┘  │
│                                  │                    │           │
│  ┌──────────────────┐  ┌────────┴─────────┐  ┌───────┴────────┐  │
│  │ Firebase Client   │  │ Database Layer   │  │ Notification   │  │
│  │ (Firestore logs)  │  │ (PostgreSQL)     │  │ Queue (Redis)  │  │
│  └──────────────────┘  └──────────────────┘  └────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### ✅ Đã hoàn thành

| STT | Công việc | Module / File | Mô tả | Trạng thái |
|:---:|-----------|---------------|-------|:----------:|
| 3.1 | **Database Connection** | `database/connection.py` | asyncpg pool + SQLite fallback | `✅` |
| 3.2 | **Data Models** | `database/models.py` | Appointment, Doctor, Schedule, TimeSlot, AuditEvent, NotificationQueue | `✅` |
| 3.3 | **Booking Service** | `services/booking_service.py` | Validation, idempotency key, optimistic locking | `✅` |
| 3.4 | **Create Booking** | `main.py → POST /api/ai/booking` | Tạo lịch hẹn mới | `✅` |
| 3.5 | **Get Booking** | `main.py → GET /api/ai/booking/{id}` | Chi tiết lịch hẹn | `✅` |
| 3.6 | **Lookup Booking** | `main.py → GET /api/ai/booking/lookup` | Tra cứu theo số điện thoại | `✅` |
| 3.7 | **Cancel Booking** | `main.py → POST /api/ai/booking/{id}/cancel` | Hủy lịch hẹn | `✅` |
| 3.8 | **Handoff Service** | `services/handoff_service.py` | Ticket creation, priority escalation | `✅` |
| 3.9 | **Handoff API** | `main.py → POST /api/ai/handoff` | Chuyển tiếp yêu cầu cho nhân viên | `✅` |
| 3.10 | **Departments API** | `main.py → GET /api/ai/departments` | 7 chuyên khoa | `✅` |
| 3.11 | **Booking Form** | `frontend/booking.html` | Form với validation đầy đủ | `✅` |
| 3.12 | **Navigation** | `frontend/*.html` | Cập nhật CTA + 6 trang | `✅` |
| 3.13 | **Firebase Client** | `services/firebase/client.py` | Conversations, feedback, audit, emergency, bookings | `✅` |
| 3.14 | **Firebase Config** | `firestore.rules`, `firestore.indexes.json` | Security rules & indexes | `✅` |
| 3.15 | **DB Migrations** | `database/migrations/001_initial_schema.sql` | Schema + indexes | `✅` |
| 3.16 | **DB Seed Data** | `database/migrations/002_seed_data.sql` | Departments, doctors, schedules, slots | `✅` |
| 3.17 | **Quick Replies** | `frontend/js/chat.js` | Handoff + cancel booking | `✅` |
| 3.18 | **Auto Handoff** | `services/chat_service.py` | Tự động handoff khi cần | `✅` |

### ❌ Chưa hoàn thành

| STT | Công việc | File dự kiến | Mô tả | Ưu tiên |
|:---:|-----------|--------------|-------|:-------:|
| 3.19 | **Redis Worker** | `services/worker.py` | Xử lý notification queue bất đồng bộ | `🔥 Cao` |
| 3.20 | **Zalo/SMS/Email Adapter** | `services/adapters/` | Gửi thông báo xác nhận, nhắc lịch | `🔥 Cao` |
| 3.21 | **Staff Dashboard** | `frontend/staff-dashboard.html` | Xem handoff tickets, quản lý booking | `📋 Trung` |
| 3.22 | **Booking History** | `frontend/history.html` | Bệnh nhân tra cứu lịch sử | `📋 Trung` |
| 3.23 | **Firebase Auth** | `services/firebase/auth.py` | OIDC/Keycloak endpoints | `📋 Trung` |
| 3.24 | **RBAC Middleware** | `services/auth_middleware.py` | patient, doctor, admin roles | `📋 Trung` |
| 3.25 | **HIS Adapter** | `services/his_adapter.py` | Kết nối Hệ thống TT Bệnh viện | `🔽 Thấp` |

---

## 🔵 Phase 4 — Production Readiness

> **Trạng thái:** `⏳ KẾ HOẠCH (0%)`
> **Mục tiêu:** Docker hóa, CI/CD, security audit

| STT | Công việc | Mô tả | Đầu ra | Ưu tiên |
|:---:|-----------|-------|--------|:-------:|
| 4.1 | **Docker Compose** | Multi-service: API + PostgreSQL + Redis + Worker | `docker-compose.yml` | `🔥 Cao` |
| 4.2 | **CI/CD Pipeline** | GitHub Actions: test, lint, build, scan, deploy | `.github/workflows/` | `🔥 Cao` |
| 4.3 | **TLS Termination** | HTTPS tại gateway | Let's Encrypt + reverse proxy | `🔥 Cao` |
| 4.4 | **WAF + Rate Limit** | Web Application Firewall | Nginx/Cloudflare | `🔥 Cao` |
| 4.5 | **Backup/Restore** | Database backup script + testing | Script + schedule | `📋 Trung` |
| 4.6 | **Secret Rotation** | Tự động rotate API keys, DB passwords | Vault / K8s Secrets | `📋 Trung` |
| 4.7 | **SLO Definition** | Service Level Objectives: uptime, latency | SLO document | `📋 Trung` |
| 4.8 | **Alerting** | PagerDuty / Opsgenie integration | Alert rules | `📋 Trung` |
| 4.9 | **Incident Runbook** | Playbook cho các sự cố thường gặp | Runbook.md | `📋 Trung` |
| 4.10 | **Penetration Testing** | Security audit bên thứ 3 | Pentest report | `📋 Trung` |
| 4.11 | **DPIA** | Đánh giá tác động dữ liệu cá nhân | DPIA document | `🔽 Thấp` |
| 4.12 | **Retention Policy** | Lifecycle: log, audit, conversation history | Policy document | `🔽 Thấp` |

---

## 🟣 Phase 5 — Future & Expansion

> **Trạng thái:** `⏳ KẾ HOẠCH (0%)`
> **Mục tiêu:** Mở rộng tính năng, đa kênh, nhiều bệnh viện

| STT | Tính năng | Mô tả | Kỹ thuật | Ưu tiên |
|:---:|-----------|-------|----------|:-------:|
| 5.1 | **🎤 Voice (STT/TTS)** | Speech-to-Text cho người già, giọng tiếng Việt | Whisper + Coqui TTS | `🔥 Cao` |
| 5.2 | **💬 Zalo OA Bot** | Kết nối Zalo Official Account | Zalo Mini App SDK | `🔥 Cao` |
| 5.3 | **📊 Analytics Dashboard** | Thống kê câu hỏi, tỷ lệ hài lòng, xu hướng | Firestore + Chart.js | `📋 Trung` |
| 5.4 | **🌐 Multi-language** | Hỗ trợ English, 中文 | LLM đa ngữ | `📋 Trung` |
| 5.5 | **🧠 Fine-tuned LLM** | Domain-specific medical model | LoRA fine-tune | `🔽 Thấp` |
| 5.6 | **🏥 Multi-hospital** | Mở rộng cho nhiều bệnh viện | Multi-tenant architecture | `🔽 Thấp` |

---

## 🐛 Bug Log

> Danh sách bug đã phát hiện và fix trong quá trình phát triển

| ID | Bug | File | Mức độ | Trạng thái |
|:--:|-----|------|:------:|:----------:|
| `B-001` | Syntax error: `from services.firebase import` incomplete do merge lỗi | `ai-service/main.py` | `CRITICAL` | `✅ FIXED` |
| `B-002` | Thiếu Firebase init step trong startup sequence | `ai-service/main.py` | `MEDIUM` | `✅ FIXED` |
| `B-003` | Thiếu `tests/__init__.py` | `tests/` | `LOW` | `✅ FIXED` |
| `B-004` | Thiếu database migration scripts | `database/migrations/` | `MEDIUM` | `✅ FIXED` |
| `B-005` | Thiếu `booking_date`, `booking_time` trong appointments table | `001_initial_schema.sql` | `MEDIUM` | `✅ FIXED` |
| `B-006` | Thiếu `env.example.txt` (file .env mẫu an toàn) | Root | `LOW` | `✅ FIXED` |

---

## 📋 File Inventory

> Danh sách toàn bộ file code trong dự án

### Backend (ai-service/)

| File | Dòng | Chức năng | Phase |
|------|:----:|-----------|:-----:|
| `main.py` | ~350 | Entry point, API routes, startup, static serve | **P1** |
| `config.py` | ~80 | Settings (NVIDIA, DB, Firebase, CORS, security) | **P1** |
| `models/schemas.py` | ~70 | Pydantic: ChatRequest, ChatResponse, HealthResponse | **P1** |
| `rag/document_loader.py` | ~120 | Load + dedup + validate knowledge documents | **P1** |
| `rag/chunker.py` | ~80 | Semantic chunking với overlap | **P1** |
| `rag/embedder.py` | ~90 | NVIDIA NIM embedding API, passage/query differentiation | **P1** |
| `rag/vector_store.py` | ~160 | ChromaDB persistent (FAISS fallback) | **P2** |
| `rag/bm25_search.py` | ~80 | BM25 sparse search | **P2** |
| `rag/hybrid_retriever.py` | ~50 | Dense + Sparse → RRF → Cross-encoder reranker | **P2** |
| `rag/retriever.py` | ~60 | Unified interface, similarity threshold, expiry check | **P1** |
| `services/chat_service.py` | ~200 | LLM orchestration, JSON extraction, citation validation | **P1** |
| `services/emergency_detector.py` | ~80 | Rule-based keyword detection (Layer 1 fail-safe) | **P1** |
| `services/rate_limiter.py` | ~60 | Sliding window: 10 requests/phút/IP | **P1** |
| `services/booking_service.py` | ~300 | Booking CRUD, validation, idempotency, optimistic locking | **P3** |
| `services/handoff_service.py` | ~120 | Ticket creation, priority-based escalation | **P3** |
| `services/firebase/client.py` | ~250 | Firestore client: conversations, messages, feedback, audit, emergency, bookings | **P3** |
| `services/firebase/schemas.py` | ~90 | Data models: Conversation, Message, Feedback, AuditLog, etc. | **P3** |
| `database/connection.py` | ~150 | asyncpg pool + SQLite fallback | **P3** |
| `database/models.py` | ~120 | Data models: Appointment, Doctor, Schedule, TimeSlot, etc. | **P3** |
| `database/migrations/001_initial_schema.sql` | ~100 | Initial schema (8 tables + indexes) | **P3** |
| `database/migrations/002_seed_data.sql` | ~70 | Seed data: departments, doctors, schedules, slots | **P3** |

### Frontend (frontend/)

| File | Dòng | Chức năng | Phase |
|------|:----:|-----------|:-----:|
| `index.html` | ~250 | Trang chủ | **P1** |
| `ai-chat.html` | ~80 | Chat AI full page | **P1** |
| `booking.html` | ~350 | Đặt lịch khám + validation | **P3** |
| `departments.html` | ~200 | Danh sách chuyên khoa | **P1** |
| `about.html` | ~150 | Giới thiệu bệnh viện | **P1** |
| `contact.html` | ~150 | Liên hệ | **P1** |
| `css/hospital-design.css` | ~800 | Design system (variables, responsive, WCAG AA) | **P1** |
| `js/chat.js` | ~300 | Chat widget, API calls, quick replies, handoff | **P1** |
| `js/app.js` | ~80 | Navigation, mobile menu, utilities | **P1** |

### Knowledge Base (knowledge/approved/)

| File | Dòng | Chức năng | Phase |
|------|:----:|-----------|:-----:|
| `manifest.json` | ~30 | Metadata: owner, approved_at, expires_at | **P2** |
| `gioi-thieu-benh-vien.md` | ~100 | Giới thiệu bệnh viện Tim Hà Nội | **P2** |
| `dich-vu-kham-chua-benh.md` | ~100 | Dịch vụ khám & chữa bệnh | **P2** |
| `lien-he-dat-lich.md` | ~100 | Liên hệ & đặt lịch | **P2** |

### Tests

| File | Dòng | Chức năng | Phase |
|------|:----:|-----------|:-----:|
| `tests/test_phase1_safety.py` | ~120 | Emergency detection, edge cases (XSS, empty, long) | **P1** |
| `tests/test_safety.py` | ~60 | Keyword matching tests | **P1** |

---

## 🚀 Hướng dẫn chạy

```bash
# === Dev mode ===
pip install -r ai-service/requirements.txt
.\start.ps1
# Website: http://localhost:8001
# API Docs: http://localhost:8001/docs

# === Run tests ===
cd ai-service
python -m pytest ../tests/ -v

# === API test examples ===
# Health
curl http://localhost:8001/api/ai/health

# Chat
curl -X POST http://localhost:8001/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Bệnh viện có khám BHYT không?"}'

# Departments
curl http://localhost:8001/api/ai/departments

# Booking
curl -X POST http://localhost:8001/api/ai/booking \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Nguyễn Văn A",
    "patient_phone": "0912345678",
    "department_id": "noi-khoa",
    "booking_date": "2026-07-20",
    "booking_time": "08:00",
    "symptoms": "Đau ngực trái"
  }'
```

---

> 🫀 *"Vì Một Trái Tim Khỏe" — Bệnh viện Tim Hà Nội*
> 
> *Tài liệu này được cập nhật tự động dựa trên source code thực tế.*
> *Cập nhật cuối: 18/07/2026*
