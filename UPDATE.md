# 📝 UPDATE — Lộ trình nâng cấp Care Assistant

> **Trạng thái:** `Đang theo dõi` **|** **Cập nhật:** `19/07/2026`
> **Mục tiêu:** Chuyển prototype Hackathon thành hệ thống pilot an toàn cho trợ lý chăm sóc khách hàng bệnh viện.

---

## 🎯 Nguyên tắc xuyên suốt

> AI chỉ trả lời thông tin có nguồn chính thức | Cấp cứu luôn được ưu tiên | Dữ liệu cá nhân được tối thiểu hóa

---

## 🟢 Phase 1 — Foundation & Safety Release Blockers

> **Trạng thái:** `✅ HOÀN THÀNH 100%` *(Đã verified toàn bộ source code)*

| # | Công việc | Module / File | Trạng thái |
|:-:|-----------|---------------|:----------:|
| 1 | FastAPI làm cổng web và API duy nhất; frontend gọi API cùng domain | `ai-service/main.py` | `✅` |
| 2 | Emergency detection fail-safe: rule-based, không đợi LLM | `services/emergency_detector.py` | `✅` |
| 3 | CORS allowlist (không wildcard) | `ai-service/main.py` | `✅` |
| 4 | Rate limiter in-memory (10 requests/phút/IP) | `services/rate_limiter.py` | `✅` |
| 5 | Security headers: X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Cache-Control | `ai-service/main.py` (middleware) | `✅` |
| 6 | Document ingestion sạch: ưu tiên `knowledge/approved/`, dedup content, bỏ file crawl | `rag/document_loader.py` | `✅` |
| 7 | Similarity threshold cố định `0.35` — không hạ ngưỡng retrieval | `rag/retriever.py` | `✅` |
| 8 | Phân biệt embedding passage (`normalize=True`) vs query (`normalize=False`) | `rag/embedder.py` | `✅` |
| 9 | URL frontend không hard-code; `safeOfficialUrl()` giới hạn domain `benhvientimhanoi.vn` | `frontend/js/chat.js` | `✅` |
| 10 | `.gitignore`, `.env.example`, unit tests (5 tests) | Root, `tests/` | `✅` |
| 11 | LLM trả JSON: `answer`, `citations`, `handoff_required`, `risk_level` | `services/chat_service.py` | `✅` |
| 12 | 6 trang giao diện: index, ai-chat, booking, departments, about, contact + Design system | `frontend/` | `✅` |
| 13 | Script khởi động `start.ps1` | Root | `✅` |

---

## 🟢 Phase 2 — Grounded RAG & Operability

> **Trạng thái:** `✅ HOÀN THÀNH 100%` *(Đã verified toàn bộ source code)*

| # | Công việc | Module / File | Trạng thái |
|:-:|-----------|---------------|:----------:|
| 1 | Xây dựng `knowledge/approved/` với content manifest (owner, approved_at, expires_at) | `knowledge/approved/manifest.json` | `✅` |
| 2 | Chuyển FAISS in-memory → ChromaDB persistent storage | `rag/vector_store.py` | `✅` |
| 3 | BM25 sparse retrieval + Reciprocal Rank Fusion (RRF) | `rag/bm25_search.py`, `rag/hybrid_retriever.py` | `✅` |
| 4 | Cross-encoder reranker (`ms-marco-MiniLM-L-6-v2`) tăng precision | `rag/hybrid_retriever.py` | `✅` |
| 5 | Citation validation trước khi trả frontend | `services/chat_service.py` | `✅` |
| 6 | Feedback workflow: user đánh giá câu trả lời (1–5 sao) | `main.py → /api/ai/feedback` | `✅` |
| 7 | Audit log ẩn danh qua Firebase (hash IP) | `services/firebase/client.py` | `✅` |
| 8 | Conversation history API: `/api/ai/conversation/{id}` | `main.py` | `✅` |
| 9 | Document expiry validation: tài liệu hết hạn không được retrieval | `rag/document_loader.py` | `✅` |

---

## 🟢 Phase 3 — Booking & Hospital Integration

> **Trạng thái:** `✅ HOÀN THÀNH 100%` *(Đã verified toàn bộ source code)*

### ✅ Đã hoàn thành

| # | Công việc | Module / File | Mức độ |
|:-:|-----------|---------------|:------:|
| 1 | Database connection layer: asyncpg pool + SQLite fallback | `database/connection.py` | `✅` |
| 2 | Data models: Appointment, Doctor, Schedule, TimeSlot, AuditEvent, NotificationQueue | `database/models.py` | `✅` |
| 3 | Booking service: validation, idempotency check, optimistic locking | `services/booking_service.py` | `✅` |
| 4 | Booking API: `POST /booking`, `GET /booking/{id}`, `POST /cancel`, `GET /lookup` | `main.py` | `✅` |
| 5 | Handoff service: ticket creation với priority-based escalation | `services/handoff_service.py` | `✅` |
| 6 | Handoff API: `POST /api/ai/handoff` | `main.py` | `✅` |
| 7 | Departments API: `GET /api/ai/departments` (7 chuyên khoa) | `main.py` | `✅` |
| 8 | Frontend booking form (`booking.html`) với validation đầy đủ | `frontend/booking.html` | `✅` |
| 9 | Navigation cập nhật (7 HTML files + CTA) | `frontend/*.html` | `✅` |
| 10 | Chat quick replies mở rộng (handoff + cancel booking) | `frontend/js/chat.js` | `✅` |
| 11 | Chat handoff tự động khi AI detect cần nhân viên | `services/chat_service.py` | `✅` |
| 12 | Dependencies: asyncpg, redis, huey, httpx | `requirements.txt` | `✅` |
| 13 | Firebase client: conversations, messages, feedback, audit_logs, emergency_logs, bookings | `services/firebase/client.py` | `✅` |
| 14 | Firebase config: `firestore.rules`, `firestore.indexes.json` | Root | `✅` |
| 15 | Database migration scripts (Initial Schema + Seed Data) | `database/migrations/` | `✅` |
| 16 | Environment template: `env.example.txt` | Root | `✅` |
| 17 | **Notification worker** (Redis worker + SMS/Zalo/Email adapters) | `services/notification_worker.py` | `✅` |
| 18 | **Staff dashboard backend** (stats, handoffs, bookings, confirm) | `services/staff_dashboard.py` | `✅` |
| 19 | **Staff dashboard frontend** (overview, handoff tickets, booking confirm) | `frontend/staff-dashboard.html` | `✅` |
| 20 | **Booking history page** (tra cứu theo SĐT, hủy lịch) | `frontend/booking-history.html` | `✅` |
| 21 | **Auto-migration runner** (chạy 001+002 khi startup) | `database/run_migrations.py` | `✅` |

> ⚠️ **Lưu ý:** Docker Compose, Dockerfile, CI/CD được đưa vào **Phase 4** (xem mục dưới).

### 🐛 Bug đã fix trong lần review gần nhất

| Bug | File | Mô tả |
|-----|------|-------|
| `🐛 CRITICAL` | `ai-service/main.py` | Syntax error: `from services.firebase import` bị incomplete do merge lỗi |
| `⚠️` | `ai-service/main.py` | Thiếu Firebase init step trong startup sequence |
| `📝` | `tests/` | Thiếu `__init__.py` |
| `📝` | `database/migrations/` | Thiếu migration scripts |
| `📝` | Root | Thiếu `env.example.txt` |
| `🐛` | `001_initial_schema.sql` | Thiếu cột `booking_date`, `booking_time` trong appointments table |

---

## 🔵 Phase 4 — Production Readiness

> **Trạng thái:** `🔄 ĐANG THỰC HIỆN (65%)`

### ✅ Đã hoàn thành

| # | Công việc | Mô tả | Module / File | Mức độ |
|:-:|-----------|-------|---------------|:------:|
| 1 | **🐳 Docker Compose** | Multi-service deployment (API + DB + Redis + Worker) | `docker-compose.yml` | `✅` |
| 2 | **📦 Dockerfile production** | Multi-stage build, gunicorn, non-root user | `Dockerfile` | `✅` |
| 3 | **🚀 CI/CD Pipeline** | GitHub Actions: lint→test→build→deploy | `.github/workflows/ci.yml` | `✅` |
| 4 | **🔄 Auto Migration** | Chạy 001+002 tự động khi startup | `database/run_migrations.py` | `✅` |

### ❌ Còn lại

| # | Công việc | Mô tả | Ưu tiên |
|:-:|-----------|-------|:-------:|
| 5 | **🔒 TLS + WAF** | Bảo mật tại gateway + rate limit | `Cao` |
| 6 | **🔄 Backup/Restore** | Database backup có kiểm thử | `Cao` |
| 7 | **🔄 Secret Rotation** | Operational security | `Trung` |
| 8 | **📊 SLO + Alerting** | Observability & cảnh báo | `Trung` |
| 9 | **📝 Incident Runbook** | Playbook cho sự cố | `Trung` |
| 10 | **🛡️ Penetration Testing** | Security audit có bên thứ 3 | `Trung` |
| 11 | **📝 DPIA** | Đánh giá tác động dữ liệu cá nhân | `Thấp` |
| 12 | **🗑️ Retention Policy** | Data lifecycle management | `Thấp` |

---

## 🟣 Phase 5 — Future & Expansion

> **Trạng thái:** `⏳ KẾ HOẠCH`

| # | Tính năng | Mô tả | Ghi chú |
|:-:|-----------|-------|:-------:|
| 1 | **🎤 Voice (STT/TTS)** | Speech-to-Text cho người già, giọng nói tiếng Việt | Cần GPU + model ASR |
| 2 | **💬 Zalo OA Chatbot** | Kết nối Zalo Official Account | Zalo Mini App |
| 3 | **📊 Analytics Dashboard** | Thống kê câu hỏi, satisfaction, xu hướng bệnh | Dựa trên Firestore data |
| 4 | **🌐 Multi-language** | Hỗ trợ tiếng Anh, tiếng Trung | LLM đa ngữ |
| 5 | **🧠 Fine-tuned Medical LLM** | Domain-specific model | Cần dataset y khoa chuyên sâu |
| 6 | **🏥 Multi-hospital** | Mở rộng cho nhiều bệnh viện | Kiến trúc multi-tenant |

---

## 📋 Tổng quan tiến độ

```
Phase 1: Foundation & Safety     [████████████████████ 100%] ✅
Phase 2: Grounded RAG            [████████████████████ 100%] ✅
Phase 3: Booking & Integration   [████████████████████ 100%] ✅
Phase 4: Production Readiness    [██████████████░░░░░░  65%] 🔄
Phase 5: Future & Expansion      [░░░░░░░░░░░░░░░░░░░░   0%] ⏳
```

---

> 🫀 *"Vì Một Trái Tim Khỏe" — Bệnh viện Tim Hà Nội*
> 
> *Cập nhật cuối: 18/07/2026 bởi nhóm phát triển AI Care Assistant*
