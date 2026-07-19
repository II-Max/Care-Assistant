# 🏥 AI Customer Care Assistant — Bệnh viện Tim Hà Nội

> **Trạng thái:** `Phase 1 ✅ → Phase 2 ✅ → Phase 3 ✅ → Phase 4 🔄 ĐANG THỰC HIỆN`
> **Cập nhật lần cuối:** 19/07/2026

---

## 📖 Giới thiệu

**AI Customer Care Assistant** là trợ lý chăm sóc khách hàng thông minh dành cho **Bệnh viện Tim Hà Nội** — bệnh viện chuyên khoa tim mạch hạng I, tuyến cuối của cả nước.

Hệ thống tích hợp trực tiếp vào website bệnh viện, giúp giải phóng nhân viên tổng đài khỏi các câu hỏi lặp lại, hỗ trợ bệnh nhân **24/7**, và **phát hiện tình huống cấp cứu tim mạch tức thì** (rule-based, không đợi LLM).

---

## 🌟 Tính năng chính

### ✅ Phase 1 — Foundation & Safety

| Tính năng | Mô tả |
|-----------|-------|
| **💬 RAG AI Chatbot** | Trả lời tự động từ Knowledge Base chính thức của bệnh viện |
| **🚨 Emergency Detection** | Rule-based: phát hiện từ khóa cấp cứu (đau ngực, khó thở, ngất xỉu) → phản hồi ngay, không đợi LLM |
| **🛡️ Trustworthy Guardrails** | AI KHÔNG chẩn đoán, không tư vấn y khoa, không hallucination |
| **📚 Citation bắt buộc** | Mọi câu trả lời đều có nguồn trích dẫn rõ ràng |
| **🏥 Website y tế** | 8 trang: Trang chủ, Chat AI, Đặt lịch, Tra cứu lịch, Dashboard NV, Chuyên khoa, Giới thiệu, Liên hệ |
| **🎨 Design system** | Giao diện chuyên nghiệp, mobile-first, WCAG 2.1 AA |

### ✅ Phase 2 — Grounded RAG & Operability

| Tính năng | Mô tả |
|-----------|-------|
| **🔍 Hybrid RAG** | Dense + BM25 + Reciprocal Rank Fusion + Cross-encoder Reranker |
| **🗄️ ChromaDB** | Chuyển từ FAISS in-memory → ChromaDB persistent storage |
| **📝 Knowledge Manifest** | Quản lý tài liệu có owner, approved_at, expires_at |
| **⭐ Feedback workflow** | Người dùng đánh giá câu trả lời 1–5 sao |

### ✅ Phase 3 — Booking & Hospital Integration

| Tính năng | Mô tả |
|-----------|-------|
| **📅 Đặt lịch khám** | Booking API với idempotency, chống trùng slot |
| **📋 Tra cứu lịch hẹn** | Tra cứu theo SĐT, hủy lịch từ frontend |
| **👨‍⚕️ Staff Dashboard** | Giao diện quản lý handoff + xác nhận booking |
| **👨‍⚕️ Handoff** | Chuyển tiếp yêu cầu phức tạp cho nhân viên |
| **🏥 Danh sách chuyên khoa** | API departments listing (7 khoa) |
| **🗄️ Database** | PostgreSQL + asyncpg (fallback SQLite tự động) |
| **📱 Notification Queue** | Worker pattern cho SMS/Zalo/Email + retry |
| **🌱 Seed Data** | 7 departments, 5 doctors, 30-day schedules |
| **☁️ Firebase Logs** | Audit, feedback, emergency logs → Firestore |

### 🔄 Đang phát triển (Phase 4 — ~65%)

| Tính năng | Mô tả |
|-----------|-------|
| **🐳 Docker Compose** | ✅ Multi-service deployment (API + PostgreSQL + Redis) |
| **📦 Dockerfile** | ✅ Multi-stage build, gunicorn, non-root user |
| **🚀 CI/CD Pipeline** | ✅ GitHub Actions (lint → test → build → deploy) |
| **🔒 TLS + WAF** | ❌ Bảo mật tại gateway |
| **🔄 Backup/Restore** | ❌ Database backup có kiểm thử |
| **📊 SLO + Alerting** | ❌ Observability & cảnh báo |

### ⏳ Kế hoạch tương lai (Phase 5+)

| Tính năng | Mô tả |
|-----------|-------|
| Auth & RBAC | OIDC/Keycloak hoặc Firebase Auth |
| Voice (STT) | Speech-to-Text cho người già |
| HIS Integration | Kết nối hệ thống thông tin bệnh viện |
| Analytics Dashboard | Thống kê câu hỏi, satisfaction, xu hướng bệnh |

---

## 🛠 Công nghệ

| Layer | Công nghệ | Trạng thái |
|-------|-----------|------------|
| **Backend** | FastAPI (Python 3.10+) | ✅ Phase 1 |
| **Frontend** | Vanilla HTML/CSS/JS (8 pages) | ✅ Phase 1 |
| **LLM** | meta/llama-3.1-70b-instruct (NVIDIA NIM) | ✅ Phase 1 |
| **Embedding** | nvidia/nv-embedqa-e5-v5 (NVIDIA NIM) | ✅ Phase 1 |
| **Vector Store** | FAISS → ChromaDB (persistent) | ✅ Phase 2 |
| **Search** | Dense → Hybrid (BM25 + RRF + reranker) | ✅ Phase 2 |
| **Database** | PostgreSQL (asyncpg) / SQLite fallback | ✅ Phase 3 |
| **Booking** | API + idempotency + optimistic locking | ✅ Phase 3 |
| **Handoff** | Ticket-based escalation | ✅ Phase 3 |
| **Staff Dashboard** | Stats overview + handoff mgmt + booking confirm | ✅ Phase 3 |
| **Notification** | Queue-based (Redis worker + templates) | ✅ Phase 3 |
| **Docker** | Multi-stage build + docker-compose | ✅ Phase 4 |
| **CI/CD** | GitHub Actions (lint → test → build → deploy) | ✅ Phase 4 |

---

## 🚀 Hướng dẫn cài đặt & chạy

### 1. Yêu cầu
- Python 3.10+
- NVIDIA NIM API Key (miễn phí tại [build.nvidia.com](https://build.nvidia.com/))
- RAM ≥ 4GB, Disk ≥ 1GB, Có Internet

### 2. Cấu hình
File `.env` đã có sẵn ở thư mục root. Mở và điền NVIDIA_API_KEY:
```ini
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxx
```
Hoặc copy từ template:
```powershell
copy .env.example .env
```

### 3. Khởi động
```powershell
.\start.ps1
```

### 4. Truy cập
| Giao diện | URL |
|-----------|-----|
| 🏠 Website chính | `http://localhost:8001` |
| 💬 Chat AI | `http://localhost:8001/ai-chat` |
| 📅 Đặt lịch | `http://localhost:8001/booking` |
| 📋 Tra cứu lịch | `http://localhost:8001/booking-history` |
| 👨‍⚕️ Dashboard NV | `http://localhost:8001/staff-dashboard` |
| 📖 API Docs (Swagger) | `http://localhost:8001/docs` |
| ❤️ Health Check | `http://localhost:8001/api/ai/health` |

---

## 📁 Cấu trúc project

```
Care-Assistant/
├── ai-service/                 # 🚀 Backend (FastAPI)
│   ├── main.py                # Entry point + tất cả API routes
│   ├── config.py              # Settings (load .env từ project root)
│   ├── requirements.txt       # Python dependencies
│   ├── models/schemas.py      # Pydantic schemas
│   ├── database/              # 🗄️ Database layer
│   │   ├── connection.py      # asyncpg pool / SQLite fallback manager
│   │   ├── models.py          # Data models (Appointment, Doctor, ...)
│   │   ├── migrations/        # SQL migration scripts
│   │   │   ├── 001_initial_schema.sql
│   │   │   └── 002_seed_data.sql
│   │   └── run_migrations.py  # Auto-migration runner (tự chạy khi startup)
│   ├── rag/                   # 🔍 RAG pipeline
│   │   ├── document_loader.py # Load từ knowledge/approved/
│   │   ├── chunker.py         # Semantic chunking (400 tokens, overlap 50)
│   │   ├── embedder.py        # NVIDIA NIM embedding
│   │   ├── vector_store.py    # ChromaDB (persistent)
│   │   ├── bm25_search.py     # BM25 sparse index
│   │   ├── hybrid_retriever.py # Dense + BM25 + RRF + Reranker
│   │   └── retriever.py       # Unified retriever interface
│   └── services/              # ⚙️ Business logic
│       ├── chat_service.py    # 💬 Core LLM chat (NVIDIA NIM)
│       ├── emergency_detector.py # 🚨 Rule-based fail-safe detection
│       ├── rate_limiter.py    # 🛡️ 10 req/min/IP (sliding window)
│       ├── booking_service.py # 📅 Booking + idempotency
│       ├── handoff_service.py # 👨‍⚕️ Staff escalation tickets
│       ├── staff_dashboard.py # 📊 Dashboard stats & management
│       ├── notification_worker.py # 📬 SMS/Zalo/Email queue worker
│       └── firebase/          # ☁️ Firebase integration (offline-safe)
├── frontend/                  # 🎨 8 trang giao diện
│   ├── index.html             # Trang chủ
│   ├── ai-chat.html           # Chat AI
│   ├── booking.html           # Đặt lịch khám
│   ├── booking-history.html   # Tra cứu & hủy lịch hẹn
│   ├── staff-dashboard.html   # Dashboard nhân viên
│   ├── departments.html       # Danh sách chuyên khoa
│   ├── about.html             # Giới thiệu bệnh viện
│   ├── contact.html           # Liên hệ
│   ├── css/hospital-design.css
│   └── js/chat.js, app.js
├── knowledge/approved/        # 📚 Knowledge Base chính thức
├── tests/                     # 🧪 Unit tests (5 safety tests)
├── plans/                     # 📋 Kế hoạch phát triển
├── .github/workflows/ci.yml   # 🚀 CI/CD Pipeline
├── docker-compose.yml         # 🐳 3 services: API + DB + Redis
├── Dockerfile                 # 📦 Multi-stage production build
├── .dockerignore              # Build context filter
├── start.ps1                  # 🚀 Local startup script
├── UPDATE.md                  # Lộ trình nâng cấp
└── README.md
```

## 📚 Tài liệu tham khảo
- [📋 Roadmap phát triển](./plans/roadmap.md)
- [🔄 Tiến độ Phase 2](./plans/phase2-progress.md)
- [🏗️ Kiến trúc & Công nghệ AI](./plans/architecture-ai.md)
- [📝 UPDATE.md — Chi tiết nâng cấp](./UPDATE.md)
- [🛡️ Defense Strategy (Hackathon)](./hackathon_defense_strategy.md)

---

> *Dự án phát triển bởi nhóm Hackathon — Bệnh viện Tim Hà Nội*
> *"Vì Một Trái Tim Khỏe" ❤️*
