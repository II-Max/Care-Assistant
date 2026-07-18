# UPDATE — Lộ trình nâng cấp Care Assistant

## Mục tiêu

Chuyển prototype Hackathon thành hệ thống có thể pilot an toàn cho trợ lý chăm sóc khách hàng bệnh viện. Mọi phase phải giữ nguyên nguyên tắc: AI chỉ trả lời thông tin có nguồn chính thức; cấp cứu luôn được ưu tiên; dữ liệu cá nhân được tối thiểu hóa.

## Phase 1 — Foundation & Safety Release Blockers

**Trạng thái: Hoàn thành trong cập nhật này**

Phạm vi:

1. Dùng FastAPI làm cổng web và API duy nhất; frontend gọi API cùng domain.
2. Chuyển nhận diện cấp cứu sang fail-safe: rule phát hiện tín hiệu nguy hiểm phản hồi ngay, không đợi LLM phủ quyết.
3. Thêm CORS allowlist, rate limit bộ nhớ và security headers cơ bản.
4. Làm sạch ingestion RAG: bỏ file crawl phụ trợ, deduplicate nội dung và ưu tiên thư mục knowledge/approved khi được đưa vào sử dụng.
5. Loại bỏ cơ chế hạ ngưỡng retrieval; không đủ bằng chứng thì từ chối/handoff.
6. Phân biệt embedding document/passages với embedding query.
7. Loại bỏ URL AI hard-code ở frontend và giới hạn link chat tới domain chính thức.
8. Bổ sung .gitignore, template môi trường và kiểm thử unit cho safety/retrieval.

Điều kiện hoàn thành:

- Browser chỉ gọi endpoint tương đối /api/ai/chat.
- Không có từ khóa cấp cứu nào phải đợi gọi LLM.
- CORS không còn wildcard.
- Loader không index media, links, metadata, contacts và tables rỗng.
- Kết quả dưới ngưỡng không được gửi vào LLM.

## Phase 2 — Grounded RAG & Operability

Phạm vi:

1. Xây dựng knowledge/approved, content manifest, owner, approved_at và expires_at cho từng tài liệu.
2. Lưu index bền vững; chuyển sang Qdrant nếu cần hybrid sparse/dense, filter metadata hoặc nhiều worker.
3. Hybrid retrieval: dense + BM25/sparse -> RRF -> reranker.
4. Ép LLM trả JSON có answer, citations, handoff_required và risk_level; xác thực citation trước khi trả frontend.
5. Thêm feedback workflow, audit log ẩn danh, OpenTelemetry, Prometheus/Grafana và dashboard RAG.
6. Tạo bộ đánh giá tối thiểu 150 câu hỏi tiếng Việt được đại diện bệnh viện duyệt.

Điều kiện hoàn thành:

- 100% câu trả lời dịch vụ có citation hoặc fallback.
- Tài liệu hết hiệu lực không được retrieval.
- Groundedness và Recall@20 được đo tự động trong CI.

## Phase 3 — Booking & Hospital Integration

Phạm vi:

1. PostgreSQL cho appointments, schedules, users và audit events.
2. Booking transaction, idempotency key và unique partial index chống trùng slot.
3. Redis + worker cho notification, indexing và outbox pattern.
4. HIS Adapter, Zalo/SMS/Email Adapter và human handoff.
5. OIDC/Keycloak hoặc Firebase Auth được backend xác thực; RBAC cho patient, doctor, admin.

Điều kiện hoàn thành:

- Không thể trùng slot khi gửi yêu cầu đồng thời.
- Người dùng/bác sĩ chỉ thấy dữ liệu đúng quyền.
- Lỗi HIS không làm mất booking event.

## Phase 4 — Production Readiness

Phạm vi:

1. Docker Compose cho môi trường tích hợp; pipeline CI chạy test, lint, type check, secret scan và container scan.
2. TLS, WAF/rate limit tại gateway, backup/restore, rotation secrets và incident runbook.
3. Đánh giá tác động dữ liệu cá nhân, retention policy, kiểm thử xâm nhập và quy trình phê duyệt nội dung y khoa.
4. SLO, cảnh báo và diễn tập sự cố.

Điều kiện hoàn thành:

- Không có PII trong log/telemetry/vector store.
- Có backup/restore được kiểm thử.
- Có quy trình xử lý nội dung sai, tài liệu hết hạn và sự cố an toàn.
