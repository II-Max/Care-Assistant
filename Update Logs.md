# Đề xuất nâng cấp cấu trúc hệ thống và công nghệ

## 1. Mục tiêu

Chuyển Care Assistant từ prototype Hackathon thành một trợ lý chăm sóc khách hàng y tế có thể pilot an toàn:

- Chỉ trả lời thông tin dịch vụ từ nguồn chính thức, có trích dẫn.
- Phát hiện tín hiệu cấp cứu theo cơ chế an toàn, không chờ LLM quyết định.
- Không làm lộ dữ liệu cá nhân hoặc endpoint nội bộ.
- Có khả năng tích hợp đặt lịch và HIS mà không phải viết lại lõi hệ thống.
- Đo lường được chất lượng, độ an toàn và độ mới của tri thức.

Phạm vi AI ở giai đoạn đầu là điều hướng dịch vụ: lịch khám, chuyên khoa, BHYT, liên hệ và quy trình. Không mở tư vấn triệu chứng tự do hoặc kê đơn.

## 2. Nhận định hiện trạng

### Điểm mạnh

- Đã có FastAPI, RAG, nguồn trích dẫn và giao diện chat.
- Có nhận diện cấp cứu và phản hồi khẩn cố định.
- Nội dung được lấy từ website/tài liệu của bệnh viện thay vì web công khai.

### Điểm cần sửa ngay

1. Frontend hiện gọi trực tiếp dịch vụ AI ở port 8001; Flask proxy không được sử dụng thực tế. Hai backend tạo thêm độ phức tạp nhưng không tăng bảo mật.
2. FastAPI đang mở CORS cho mọi origin; Flask cũng mở CORS và chạy debug. Đây là cấu hình chỉ phù hợp localhost.
3. Data có 224 file Markdown, gồm nhiều metadata, links, media, contacts và tables rỗng; 132 tệp có nội dung trùng. Loader lại index tất cả file Markdown.
4. Khi có từ khóa cấp cứu, hệ thống vẫn đợi LLM phân loại. LLM có thể trả NORMAL hoặc timeout, gây nguy cơ bỏ qua cảnh báo.
5. RAG dùng một ngưỡng cosine cố định và còn hạ ngưỡng khi không tìm thấy kết quả tốt. Điều này làm suy yếu nguyên tắc từ chối khi không đủ bằng chứng.
6. Index FAISS tạo lại khi khởi động, chưa có phiên bản tri thức, persistence, phê duyệt nội dung hoặc kiểm tra độ mới.
7. Fallback embedding all-MiniLM-L6-v2 không tối ưu cho tiếng Việt. Embedding tài liệu hiện gửi với input type query thay vì passage/document.
8. Chat frontend tự render Markdown và URL sinh ra từ phản hồi AI; cần sanitizer và allowlist domain để tránh XSS.
9. Chưa có rate limit, auth/session, audit log, test suite, .gitignore, CI/CD hay dependency lockfile.

## 3. Kiến trúc mục tiêu

    Người dùng
        -> Website
        -> API Gateway / FastAPI
        -> Safety Gateway
             -> Luồng cấp cứu: phản hồi cố định, hotline, CTA gọi ngay
             -> Luồng dịch vụ: Knowledge Service -> RAG -> LLM
             -> Luồng đặt lịch: Booking Service -> PostgreSQL -> HIS Adapter
        -> Audit log, metrics, tracing

### Quyết định kiến trúc

- Dùng một FastAPI modular monolith làm backend duy nhất. Không giữ Flask chỉ để proxy.
- Frontend chỉ gọi API cùng domain, ví dụ /api/v1/chat. Không biết URL của LLM, Qdrant hay HIS.
- Tách các module theo domain nghiệp vụ, nhưng chưa tách thành microservice. Microservice chỉ cần khi từng module có tải, quyền vận hành hoặc chu kỳ phát hành độc lập.
- Dùng hàng đợi nền cho indexing, gửi thông báo và đồng bộ HIS.

## 4. Danh sách thay đổi bắt buộc

| Ưu tiên | Thay đổi | Lý do và tiêu chí hoàn thành |
|---|---|---|
| P0 | Gộp Flask và FastAPI thành FastAPI API/BFF duy nhất. | Frontend dùng đường dẫn tương đối; không còn cổng 8001 bị lộ ra browser. |
| P0 | Tạo Safety Gateway đứng trước mọi xử lý AI. | Mọi tin nhắn đều đi qua kiểm tra cấp cứu, PII, ý định và prompt-injection trước retrieval. |
| P0 | Emergency detector phải fail-safe. | Từ điển/regex có tín hiệu nguy hiểm sẽ trả cảnh báo ngay; LLM không được quyền hạ mức EMERGENCY xuống NORMAL. |
| P0 | Tách dữ liệu thành raw, approved và manifest. | Chỉ thư mục approved được index; raw dùng cho kiểm duyệt và truy vết. |
| P0 | Loại dữ liệu rác, deduplicate theo SHA-256 và lập content manifest. | Không index metadata, media, links, contacts lặp hoặc bảng rỗng. |
| P0 | Không dùng kết quả dưới ngưỡng. | Thiếu bằng chứng, tài liệu hết hạn hoặc nguồn không được duyệt phải handoff/hotline. |
| P0 | Khóa CORS, tắt debug, thêm rate limit và request ID. | Production chỉ chấp nhận domain được phép; API có giới hạn theo IP/session. |
| P0 | Render phản hồi AI an toàn. | Sanitizer HTML, allowlist URL nguồn bệnh viện và rel=noopener cho link mới. |
| P0 | Thêm .gitignore, .env.example và quét secret trong CI. | Không commit API key, index local, log hay dữ liệu nhạy cảm. |
| P1 | Chuyển RAG sang hybrid retrieval. | Kết hợp dense embedding và sparse/BM25, sau đó RRF và rerank để bắt chính xác thuật ngữ BHYT, tên khoa, giá. |
| P1 | Version hóa Knowledge Base. | Mỗi chunk có source_id, URL chính thức, owner, approved_at, effective_from và expires_at. |
| P1 | LLM trả JSON có kiểm soát. | Schema gồm answer, citations, handoff_required, risk_level; câu trả lời thiếu citation bị từ chối. |
| P1 | Dùng PostgreSQL cho đặt lịch thật. | Transaction và unique partial index chống trùng slot; không ghi lịch khám trực tiếp từ client. |
| P1 | Thêm Redis và worker. | Indexing, SMS/Zalo/email và đồng bộ HIS chạy nền, không chặn API chat. |
| P1 | Ẩn danh/loại PII trước khi gọi mô hình ngoài. | Không gửi số điện thoại, email, CCCD hoặc dữ liệu bệnh án sang nhà cung cấp LLM khi chưa có cơ sở phê duyệt. |
| P2 | Tạo HIS Adapter và Notification Adapter. | Core không phụ thuộc vendor cụ thể, dễ thay đổi HIS, Zalo, SMS hay email. |
| P2 | Tạo human handoff và feedback workflow. | Câu hỏi thiếu dữ liệu thành ticket có kiểm soát thay vì câu từ chối cụt. |
| P2 | Monitoring và đánh giá RAG liên tục. | Theo dõi p95 latency, tỷ lệ fallback, source freshness, groundedness và lỗi cấp cứu. |

## 5. Luồng thuật toán đề xuất

### 5.1 Safety Gateway

1. Chuẩn hóa Unicode, lỗi gõ tiếng Việt và giới hạn độ dài input.
2. Phát hiện PII bằng regex và rule riêng cho số điện thoại, email, CCCD; giảm thiểu dữ liệu gửi sang mô hình ngoài.
3. Phát hiện cấp cứu bằng danh sách từ khóa/biểu thức chính quy đã được bác sĩ duyệt.
4. Nếu emergency: trả phản hồi cố định có nút gọi 115, hotline và địa chỉ cấp cứu. Không gọi LLM.
5. Phân loại intent: service FAQ, đặt lịch, tình trạng sức khỏe, ngoài phạm vi.
6. Tình trạng sức khỏe không khẩn cấp: khuyến nghị kênh bác sĩ/hotline, không chẩn đoán hoặc đưa thuốc.

### 5.2 RAG có bằng chứng

1. Hybrid retrieve 20 ứng viên bằng dense vector và sparse/BM25.
2. Dùng Reciprocal Rank Fusion để gộp ranking.
3. Rerank 20 ứng viên, giữ tối đa 3 đến 4 chunks từ tài liệu đã approved và còn hiệu lực.
4. Kiểm tra confidence, score gap, độ mới của tài liệu và nguồn.
5. Nếu không đạt điều kiện: trả lời theo mẫu handoff, không gọi LLM.
6. Nếu đạt: LLM chỉ tổng hợp từ context, trả JSON có citation theo source_id.
7. Validator kiểm tra citation trước khi API gửi phản hồi về frontend.

Thông số khởi đầu cần benchmark bằng bộ câu hỏi thật:

- Chunk theo heading/FAQ, khoảng 300 đến 450 token, overlap 40 đến 60 token.
- Retrieve top 20, rerank còn top 4, đưa tối đa 3 chunks vào context.
- Không chốt similarity threshold toàn cục; hiệu chỉnh theo intent và đánh giá offline.

### 5.3 Đặt lịch

1. Client gửi yêu cầu tới API đã xác thực.
2. Backend kiểm tra quyền, lịch bác sĩ, thời gian nghỉ, slot và idempotency key.
3. PostgreSQL transaction tạo appointment và giữ slot.
4. Unique partial index trên doctor_id và start_at đảm bảo chỉ một lịch đang giữ/xác nhận.
5. Outbox event gửi thông báo hoặc đồng bộ HIS bằng worker.
6. Người dùng và bác sĩ chỉ truy cập lịch đúng quyền được phân công.

## 6. Công nghệ đề xuất

| Layer | Công nghệ | Lý do |
|---|---|---|
| API | FastAPI + Pydantic + SQLAlchemy | Một API typed, validation rõ, tự sinh OpenAPI, phù hợp Python AI. |
| Reverse proxy | Nginx hoặc Traefik | TLS, giới hạn request, static assets và route API cùng domain. |
| RAG MVP | FAISS persisted trên disk | Đủ nhanh và tiết kiệm cho vài nghìn chunks sau khi dữ liệu được làm sạch. |
| RAG production | Qdrant | Hỗ trợ hybrid sparse/dense, filter metadata và persistence tốt hơn. |
| Embedding | BAAI/bge-m3, benchmark với tiếng Việt bệnh viện | Đa ngôn ngữ, hỗ trợ retrieval dense/sparse; không dùng fallback chỉ tối ưu tiếng Anh. |
| Reranker | bge-reranker-v2-m3 hoặc model đã benchmark | Tăng chất lượng chọn context trước LLM. |
| LLM | Mô hình instruct được benchmark bằng bộ câu hỏi nội bộ; ưu tiên triển khai private/on-prem khi có PII | Không chọn model chỉ từ benchmark chung; đánh giá tiếng Việt, grounding, latency và chính sách dữ liệu. |
| Database | PostgreSQL | Transaction, unique constraint, audit và schema quan hệ cho lịch hẹn. |
| Cache/queue | Redis + Celery hoặc Dramatiq | Tác vụ nền cho indexing, thông báo và tích hợp. |
| Object storage | MinIO/S3 | Lưu tài liệu nguồn, manifest, version KB và artifact đánh giá. |
| Auth | OIDC/Keycloak; hoặc Firebase Auth được backend xác thực token | Chỉ dùng một nguồn danh tính và role, không tự phát hành thêm JWT song song. |
| Observability | OpenTelemetry + Prometheus/Grafana + Loki | Metrics, tracing, cảnh báo và log có ẩn danh. |
| Frontend security | DOMPurify + Content Security Policy | Chặn XSS khi hiển thị nội dung AI hoặc link nguồn. |
| Delivery | Docker Compose cho dev, CI với pytest/ruff/mypy/secret scan | Tái lập môi trường và chặn lỗi trước khi deploy. |

## 7. Cấu trúc repository đề xuất

    care-assistant/
    ├── apps/
    │   └── web/
    ├── services/
    │   └── api/
    │       ├── main.py
    │       ├── modules/
    │       │   ├── chat/
    │       │   ├── safety/
    │       │   ├── knowledge/
    │       │   ├── booking/
    │       │   ├── integrations/
    │       │   └── audit/
    │       ├── workers/
    │       └── repositories/
    ├── knowledge/
    │   ├── raw/
    │   ├── approved/
    │   ├── manifests/
    │   └── evaluations/
    ├── infra/
    │   ├── docker-compose.yml
    │   ├── nginx/
    │   └── monitoring/
    ├── tests/
    │   ├── unit/
    │   ├── integration/
    │   ├── safety/
    │   └── rag_evaluation/
    ├── .env.example
    ├── .gitignore
    └── pyproject.toml

## 8. Tiêu chí nghiệm thu mức xuất sắc

- 100% phản hồi dịch vụ có nguồn chính thức hoặc từ chối trả lời.
- 100% case cấp cứu trong bộ test được chuyển sang luồng khẩn cấp; không dùng LLM để phủ quyết luật cấp cứu.
- 0 trường hợp trùng lịch ở kiểm thử đồng thời.
- 0 PII trong log, telemetry và vector database; có chính sách retention rõ ràng.
- 100% tài liệu được index có chủ sở hữu, URL, thời điểm duyệt và ngày hết hiệu lực.
- Có bộ benchmark tối thiểu 150 đến 300 câu hỏi tiếng Việt do đại diện bệnh viện duyệt.
- Đạt mục tiêu pilot: Recall@20 >= 95%, câu trả lời grounded >= 95%, tỷ lệ citation hợp lệ 100%.
- Có test unit, integration, security, safety và CI bắt buộc trước merge.
- API p95 dưới 3 giây cho FAQ thường; khi LLM lỗi, trả handoff trong giới hạn timeout đã định.

## 9. Thứ tự triển khai

### Đợt 1 - Release blocker

1. Gộp API, đóng CORS/debug, đổi frontend sang API cùng domain.
2. Fail-safe emergency gateway.
3. Làm sạch và version hóa Knowledge Base.
4. Chặn weak retrieval, thêm citation validation.
5. Chống XSS, .gitignore, env template và rate limit.
6. Viết bộ test safety/RAG tối thiểu.

### Đợt 2 - Pilot an toàn

1. Hybrid retrieval, reranker và Qdrant hoặc FAISS persisted.
2. Audit log, metrics, dashboard và feedback workflow.
3. PostgreSQL/Redis cho đặt lịch và worker.
4. Human handoff, thông báo và adapter tích hợp.

### Đợt 3 - Production

1. Kết nối HIS theo adapter, phân quyền OIDC và kiểm thử xâm nhập.
2. Quy trình phê duyệt nội dung cùng đơn vị chuyên môn.
3. Đánh giá dữ liệu cá nhân, chính sách retention và phương án triển khai mô hình riêng.
4. Monitoring SLA, backup/restore và diễn tập incident response.

## 10. Kết luận

Mục tiêu không phải thêm nhiều microservice hoặc một LLM lớn hơn. Kiến trúc xuất sắc phải làm được ba việc: chặn nguy cơ trước AI, chỉ cho AI trả lời khi có bằng chứng chính thức, và giữ toàn bộ dữ liệu/tích hợp dưới quyền kiểm soát của bệnh viện. Thứ tự ưu tiên là an toàn và chất lượng tri thức trước, tính năng nâng cao sau.
