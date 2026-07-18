# 🔄 Phase 3 — Booking & Hospital Integration

## Theo dõi tiến độ chi tiết

> **Project:** AI Customer Care Assistant — Bệnh viện Tim Hà Nội
> **Bắt đầu:** 18/07/2026
> **Target hoàn thành:** 31/07/2026

---

## 📋 Checklist

### 🏗️ Backend Infrastructure

| STT | Công việc | Trạng thái | File | Ghi chú |
|-----|-----------|------------|------|---------|
| 1.1 | ✅ Database connection layer (asyncpg + SQLite fallback) | ✅ **Done** | `database/connection.py` | |
| 1.2 | ✅ Data models (Appointment, Doctor, Schedule, TimeSlot, ...) | ✅ **Done** | `database/models.py` | |
| 1.3 | ✅ Database initialization in startup | ✅ **Done** | `main.py` lifespan | |
| 1.4 | ⏳ Database migration system | ⏳ | `database/migrations/` | Cần tạo |
| 1.5 | ⏳ Connection pooling config | ⏳ | `.env` | Thêm DB_* vars |

### 📅 Booking API

| STT | Công việc | Trạng thái | File | Ghi chú |
|-----|-----------|------------|------|---------|
| 2.1 | ✅ Booking service (validation, idempotency, optimistic locking) | ✅ **Done** | `services/booking_service.py` | |
| 2.2 | ✅ POST /api/ai/booking — Tạo booking | ✅ **Done** | `main.py` | |
| 2.3 | ✅ GET /api/ai/booking/{id} — Tra cứu lịch hẹn | ✅ **Done** | `main.py` | |
| 2.4 | ✅ POST /api/ai/booking/{id}/cancel — Hủy lịch hẹn | ✅ **Done** | `main.py` | |
| 2.5 | ✅ GET /api/ai/booking/lookup?phone=xxx — Tra cứu theo SĐT | ✅ **Done** | `main.py` | |
| 2.6 | ✅ GET /api/ai/departments — Danh sách chuyên khoa | ✅ **Done** | `main.py` | |

### 👨‍⚕️ Handoff System

| STT | Công việc | Trạng thái | File | Ghi chú |
|-----|-----------|------------|------|---------|
| 3.1 | ✅ Handoff service (ticket creation, priority, notification) | ✅ **Done** | `services/handoff_service.py` | |
| 3.2 | ✅ POST /api/ai/handoff — Tạo handoff ticket | ✅ **Done** | `main.py` | |
| 3.3 | ✅ Frontend handoff trigger (chat button + auto-detection) | ✅ **Done** | `chat.js` | |
| 3.4 | ⏳ Staff dashboard for handoff tickets | ⏳ | `frontend/admin.html` | Phase 4 |

### 🏥 Frontend Booking

| STT | Công việc | Trạng thái | File | Ghi chú |
|-----|-----------|------------|------|---------|
| 4.1 | ✅ Booking form page với validation | ✅ **Done** | `frontend/booking.html` | |
| 4.2 | ✅ Booking success view | ✅ **Done** | `frontend/booking.html` | |
| 4.3 | ✅ Navigation cập nhật (all pages) | ✅ **Done** | All HTML files | |
| 4.4 | ⏳ Booking history page cho bệnh nhân | ⏳ | `frontend/lich-su.html` | Phase 4 |
| 4.5 | ⏳ Admin booking management | ⏳ | `frontend/admin-booking.html` | Phase 4 |

### 📱 Notification System

| STT | Công việc | Trạng thái | File | Ghi chú |
|-----|-----------|------------|------|---------|
| 5.1 | ✅ Notification queue in database (PG schema) | ✅ **Done** | `database/models.py` | |
| 5.2 | ✅ Notification enqueue in booking service | ✅ **Done** | `booking_service.py` | |
| 5.3 | ⏳ Redis worker for async notifications | ⏳ | `workers/notification_worker.py` | Cần tạo |
| 5.4 | ⏳ Zalo adapter | ⏳ | `adapters/zalo.py` | Cần tích hợp |
| 5.5 | ⏳ SMS adapter | ⏳ | `adapters/sms.py` | Cần tích hợp |
| 5.6 | ⏳ Email adapter | ⏳ | `adapters/email.py` | Cần tích hợp |

### 🔐 Auth & RBAC

| STT | Công việc | Trạng thái | File | Ghi chú |
|-----|-----------|------------|------|---------|
| 6.1 | 🟡 Firebase Auth verification (verify_token) | 🟡 Partial | `firebase/client.py` | Có method, chưa có endpoint |
| 6.2 | ⏳ OIDC/Keycloak integration | ⏳ | | Phase 4 |
| 6.3 | ⏳ RBAC middleware | ⏳ | `middleware/auth.py` | Phase 4 |
| 6.4 | ⏳ User registration/login UI | ⏳ | | Phase 4 |

### 🗄️ Database Implementation

| STT | Công việc | Trạng thái | File | Ghi chú |
|-----|-----------|------------|------|---------|
| 7.1 | 🟡 PostgreSQL schema SQL | 🟡 Partial | `database/models.py` | Models exist, cần migrate script |
| 7.2 | ⏳ Initial migration file | ⏳ | `database/migrations/001_init.sql` | |
| 7.3 | ⏳ Seed data for departments & doctors | ⏳ | `database/seed.py` | |
| 7.4 | ⏳ Indexes for performance | ⏳ | `database/migrations/002_indexes.sql` | |

### 📦 Dependencies

| STT | Package | Version | Status | Ghi chú |
|-----|---------|---------|--------|---------|
| 8.1 | asyncpg | >=0.29.0 | ✅ Added | PostgreSQL driver |
| 8.2 | redis | >=5.0.0 | ✅ Added | Notification queue |
| 8.3 | huey | >=2.5.0 | ✅ Added | Background worker |
| 8.4 | httpx | >=0.25.0 | ✅ Added | HIS adapter HTTP client |

---

## 🎯 Key Metrics cho Phase 3

| Metric | Target | Hiện tại | Ghi chú |
|--------|--------|----------|---------|
| **Booking success rate** | > 99% | — | Cần monitoring |
| **Idempotency blocking rate** | 100% | — | Không trùng booking |
| **Handoff response time** | < 5 phút | — | Cần staff dashboard |
| **Slot booking conflict** | 0% | — | Optimistic locking |
| **API response time (p95)** | < 500ms | — | Cho booking endpoints |

---

## 📂 File thay đổi trong Phase 3

```
ai-service/
├── main.py                       → Thêm booking, handoff, departments endpoints
├── requirements.txt              → Thêm asyncpg, redis, huey, httpx
├── services/
│   ├── booking_service.py        → NEW: Booking logic + validation
│   └── handoff_service.py        → NEW: Handoff ticket system
├── database/
│   ├── connection.py             → ✅ Existing: asyncpg pool
│   ├── models.py                 → ✅ Existing: data models
│   └── __init__.py               → ✅ Existing

frontend/
├── booking.html                  → NEW: Booking form page
├── index.html                    → ✅ Updated navigation
├── ai-chat.html                  → ✅ Updated navigation
├── departments.html              → ✅ Updated navigation
├── contact.html                  → ✅ Updated navigation
├── about.html                    → ✅ Updated navigation
└── js/chat.js                    → ✅ Updated handoff + quick replies

plans/
└── phase3-progress.md            → NEW: This file
```

## 🚧 Blockers & Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| PostgreSQL chưa có sẵn | Medium | SQLite fallback — vẫn chạy được |
| Redis chưa cấu hình | Low | Notification queue dùng PG/SQLite tạm |
| Firebase Auth complexity | Medium | Có thể dùng simple token cho MVP |
| HIS Adapter phụ thuộc đối tác | High | Tạo adapter interface trước, implement sau |
