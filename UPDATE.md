# UPDATE — Lộ trình nâng cấp Care Assistant

## Mục tiêu

Chuyển prototype Hackathon thành hệ thống có thể pilot an toàn cho trợ lý chăm sóc khách hàng bệnh viện. Mọi phase phải giữ nguyên nguyên tắc: AI chỉ trả lời thông tin có nguồn chính thức; cấp cứu luôn được ưu tiên; dữ liệu cá nhân được tối thiểu hóa.

## Phase 1 — Foundation & Safety Release Blockers

**Trạng thái: ✅ Hoàn thành**

Phạm vi:

1. Dùng FastAPI làm cổng web và API duy nhất; frontend gọi API cùng domain.
2. Chuyển nhận diện cấp cứu sang fail-safe: rule phát hiện tín hiệu nguy hiểm phản hồi ngay, không đợi LLM phủ quyết.
3. Thêm CORS allowlist, rate limit bộ nhớ và security headers cơ bản.
4. Làm sạch ingestion RAG: bỏ file crawl phụ trợ, deduplicate nội dung và ưu tiên thư mục knowledge/approved khi được đưa vào sử dụng.
5. Loại bỏ cơ chế hạ ngưỡng retrieval; không đủ bằng chứng thì từ chối/handoff.
6. Phân biệt embedding document/passages với embedding query.
7. Loại bỏ URL AI hard-code ở frontend và giới hạn link chat tới domain chính thức.
8. Bổ sung .gitignore, template môi trường và kiểm thử unit cho safety/retrieval.

## Phase 2 — Grounded RAG & Operability

**Trạng thái: ✅ Hoàn thành**

Phạm vi:

1. Xây dựng knowledge/approved, content manifest, owner, approved_at và expires_at cho từng tài liệu.
2. Lưu index bền vững; chuyển sang ChromaDB cho hybrid sparse/dense, filter metadata và persistent storage.
3. Hybrid retrieval: dense + BM25/sparse -> RRF -> reranker (cross-encoder/ms-marco-MiniLM-L-6-v2).
4. Ép LLM trả JSON có answer, citations, handoff_required và risk_level; xác thực citation trước khi trả frontend.
5. Thêm feedback workflow, audit log ẩn danh.
6. Tạo bộ đánh giá tối thiểu 150 câu hỏi tiếng Việt được đại diện bệnh viện duyệt.

## Phase 3 — Booking & Hospital Integration

**Trạng thái: 🔄 Đang thực hiện**

Phạm vi:

1. PostgreSQL cho appointments, schedules, users và audit events.
2. Booking transaction, idempotency key và optimistic locking chống trùng slot.
3. Redis + worker cho notification, indexing.
4. HIS Adapter, Zalo/SMS/Email Adapter và human handoff.
5. OIDC/Keycloak hoặc Firebase Auth được backend xác thực; RBAC cho patient, doctor, admin.

### Đã hoàn thành trong Phase 3:

- [x] Database connection layer (asyncpg + SQLite fallback)
- [x] Data models (Appointment, Doctor, Schedule, TimeSlot, AuditEvent, NotificationQueue)
- [x] Booking service: validation, idempotency check, optimistic locking
- [x] Booking API: POST /api/ai/booking, GET /api/ai/booking/{id}, POST cancel, GET lookup
- [x] Handoff service: ticket creation với priority-based escalation
- [x] Handoff API: POST /api/ai/handoff
- [x] Departments API: GET /api/ai/departments
- [x] Frontend booking form (booking.html) với validation đầy đủ
- [x] Navigation cập nhật (thêm booking link)
- [x] Chat quick replies mở rộng (handoff + cancel booking)
- [x] Chat handoff tự động khi AI detect cần nhân viên
- [x] Thêm dependencies: asyncpg, redis, huey, httpx

### Còn lại:

- [ ] Redis worker for notification queue
- [ ] Zalo/SMS/Email adapter
- [ ] Database migration scripts
- [ ] Seed data (departments, doctors)
- [ ] Staff dashboard for handoff tickets
- [ ] Booking history page
- [ ] Firebase Auth endpoints
- [ ] RBAC middleware
- [ ] HIS Adapter

## Phase 4 — Production Readiness (Kế hoạch)

Phạm vi:

1. Docker Compose cho môi trường tích hợp; pipeline CI chạy test, lint, type check, secret scan và container scan.
2. TLS, WAF/rate limit tại gateway, backup/restore, rotation secrets và incident runbook.
3. Đánh giá tác động dữ liệu cá nhân, retention policy, kiểm thử xâm nhập và quy trình phê duyệt nội dung y khoa.
4. SLO, cảnh báo và diễn tập sự cố.
