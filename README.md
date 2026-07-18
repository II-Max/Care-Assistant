# 🏥 AI Customer Care Assistant — Bệnh viện Tim Hà Nội

> **Trạng thái:** `Phase 1 ✅` → `Phase 2 ✅` → `Phase 3 🔄 ĐANG THỰC HIỆN`
> **Cập nhật lần cuối:** 18/07/2026

---

## 📖 Giới thiệu

**AI Customer Care Assistant** là trợ lý chăm sóc khách hàng thông minh dành cho **Bệnh viện Tim Hà Nội** — bệnh viện chuyên khoa tim mạch hạng I, tuyến cuối của cả nước.

Hệ thống tích hợp trực tiếp vào website bệnh viện, giúp giải phóng nhân viên tổng đài khỏi các câu hỏi lặp lại, hỗ trợ bệnh nhân **24/7**, và **phát hiện tình huống cấp cứu tim mạch trong 1ms** — không đợi AI sinh text chậm.

---

## 🌟 Tính năng chính

### ✅ Hiện tại (Phase 1)

| Tính năng | Mô tả |
|-----------|-------|
| **💬 RAG AI Chatbot** | Trả lời tự động từ Knowledge Base chính thức của bệnh viện |
| **🚨 Emergency Detection** | Phát hiện từ khóa cấp cứu (đau ngực, khó thở, ngất xỉu) → phản hồi ngay lập tức |
| **🛡️ Trustworthy Guardrails** | AI KHÔNG chẩn đoán, không tư vấn y khoa, không hallucination |
| **📚 Citation bắt buộc** | Mọi câu trả lời đều có nguồn trích dẫn rõ ràng |
| **🏥 Website y tế** | 5 trang: Trang chủ, Chat AI, Chuyên khoa, Giới thiệu, Liên hệ |
| **🎨 Design system** | Giao diện chuyên nghiệp, mobile-first, WCAG 2.1 AA |

### 🔄 Đang phát triển (Phase 3)

| Tính năng | Mô tả |
|-----------|-------|
| **📅 Đặt lịch khám** | Booking API với idempotency, chống trùng slot |
| **📋 Tra cứu lịch hẹn** | Tìm kiếm theo số điện thoại, hủy lịch |
| **👨‍⚕️ Handoff** | Chuyển tiếp yêu cầu phức tạp cho nhân viên |
| **🏥 Danh sách chuyên khoa** | API departments listing |
| **🗄️ Database** | PostgreSQL + asyncpg (fallback SQLite) |
| **📱 Notification Queue** | Worker pattern cho Zalo/SMS/Email |

### ⏳ Kế hoạch tương lai (Phase 4+)

| Tính năng | Mô tả |
|-----------|-------|
| Auth & RBAC | OIDC/Keycloak hoặc Firebase Auth |
| Docker + CI/CD | Production deployment |
| Voice (STT) | Speech-to-Text cho người già |
| HIS Integration | Kết nối hệ thống thông tin bệnh viện |

---

## 🛠 Công nghệ

| Layer | Công nghệ | Trạng thái |
|-------|-----------|------------|
| **Backend** | FastAPI (Python 3.10+) | ✅ Phase 1 |
| **Frontend** | Vanilla HTML/CSS/JS | ✅ Phase 1 |
| **LLM** | meta/llama-3.1-70b-instruct (NVIDIA NIM) | ✅ Phase 1 |
| **Embedding** | nv-embedqa-e5-v5 (NVIDIA NIM) | ✅ Phase 1 |
| **Vector Store** | FAISS → ChromaDB (persistent) | ✅ Phase 2 |
| **Search** | Dense → Hybrid (BM25 + RRF + reranker) | ✅ Phase 2 |
| **Database** | PostgreSQL (asyncpg) / SQLite fallback | 🔄 Phase 3 |
| **Booking** | API + idempotency + optimistic locking | 🔄 Phase 3 |
| **Handoff** | Ticket-based escalation | 🔄 Phase 3 |
| **Notification** | Queue-based (Redis worker) | 🔄 Phase 3 |

---

## 🚀 Hướng dẫn cài đặt & chạy

### 1. Yêu cầu
- Python 3.10+
- NVIDIA NIM API Key

### 2. Cấu hình
```bash
cp .env.example .env
```
Mở `.env` và thêm:
```
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxx
```

### 3. Khởi động
```powershell
.\start.ps1
```

### 4. Truy cập
- **Website:** `http://localhost:8001` (FastAPI serve cả API + static)
- **API Docs:** `http://localhost:8001/docs`

---

## 📁 Cấu trúc project

```
├── ai-service/              # 🚀 Backend (FastAPI)
│   ├── main.py             # Entry point
│   ├── config.py           # Settings
│   ├── models/             # Pydantic schemas
│   ├── database/           # 🗄️ PostgreSQL + SQLite fallback
│   │   ├── connection.py   # asyncpg pool manager
│   │   └── models.py       # Data models (appointments, users, ...)
│   ├── rag/                # 🔍 RAG pipeline
│   │   ├── document_loader.py
│   │   ├── chunker.py
│   │   ├── embedder.py
│   │   ├── vector_store.py
│   │   ├── bm25_search.py
│   │   ├── hybrid_retriever.py
│   │   └── retriever.py
│   └── services/           # ⚙️ Business logic
│       ├── emergency_detector.py
│       ├── chat_service.py
│       ├── rate_limiter.py
│       ├── booking_service.py   # 📅 Đặt lịch khám
│       ├── handoff_service.py   # 👨‍⚕️ Chuyển tiếp nhân viên
│       └── firebase/            # ☁️ Firebase integration
│           ├── client.py
│           └── schemas.py
├── frontend/               # 🎨 Giao diện
│   ├── index.html, ai-chat.html
│   ├── booking.html, departments.html
│   ├── contact.html, about.html
│   ├── css/hospital-design.css
│   └── js/chat.js, app.js
├── knowledge/
│   └── approved/           # 📚 Knowledge Base chính thức
│       ├── gioi-thieu-benh-vien.md
│       ├── dich-vu-kham-chua-benh.md
│       └── lien-he-dat-lich.md
├── Data/                   # Raw data (archive)
├── tests/                  # 🧪 Unit tests
├── plans/                  # 📋 Kế hoạch phát triển
│   ├── roadmap.md          # Lộ trình tổng thể
│   ├── phase2-progress.md  # Theo dõi Phase 2
│   └── architecture-ai.md  # Kiến trúc hệ thống
├── start.ps1               # 🚀 Khởi động
├── UPDATE.md               # Lộ trình nâng cấp
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
