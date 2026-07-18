# 🔄 Phase 2 — Grounded RAG & Operability

## Theo dõi tiến độ chi tiết

> **Project:** AI Customer Care Assistant — Bệnh viện Tim Hà Nội
> **Bắt đầu:** 18/07/2026
> **Target hoàn thành:** 25/07/2026

---

## 📋 Checklist hàng ngày

### Ngày 1 — Knowledge Management (18/07)

| STT | Công việc | Trạng thái | Người thực hiện | Ghi chú |
|-----|-----------|------------|-----------------|---------|
| 1.1 | ✅ Dọn dẹp Data/ — xóa scrap artifacts | ✅ **Done** | System | 150+ file rác đã loại bỏ |
| 1.2 | ✅ Cô đọng nội dung thành 3 file knowledge | ✅ **Done** | System | 3 file: Giới thiệu, Dịch vụ, Liên hệ |
| 1.3 | ✅ Tạo `knowledge/approved/` | ✅ **Done** | System | Thư mục chính thức |
| 1.4 | 🔄 Tạo manifest.json (owner, approved_at, expires_at) | 🔄 **In Progress** | | Cần định nghĩa schema |
| 1.5 | Cập nhật DocumentLoader ưu tiên `knowledge/approved/` | ⏳ | | |

### Ngày 2 — Persistent Vector Store (19/07)

| STT | Công việc | Trạng thái | Ghi chú |
|-----|-----------|------------|---------|
| 2.1 | Cài đặt ChromaDB + dependencies | ⏳ | `pip install chromadb` |
| 2.2 | Refactor VectorStore → ChromaDB | ⏳ | Giữ interface cũ |
| 2.3 | Lưu index xuống disk (`chroma_db/`) | ⏳ | |
| 2.4 | Cache embedding để không re-embed mỗi lần | ⏳ | |
| 2.5 | Test: restart → không mất index | ⏳ | |

### Ngày 3 — Hybrid Retrieval (20/07)

| STT | Công việc | Trạng thái | Ghi chú |
|-----|-----------|------------|---------|
| 3.1 | Cài đặt BM25 (rank_bm25) | ⏳ | |
| 3.2 | Tạo HybridRetriever class | ⏳ | Kế thừa từ Retriever |
| 3.3 | Implement RRF fusion | ⏳ | k=60 |
| 3.4 | Cài đặt Cross-encoder reranker | ⏳ | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| 3.5 | Test: so sánh precision với dense-only | ⏳ | |

### Ngày 4 — Citation Validation & Response Quality (21/07)

| STT | Công việc | Trạng thái | Ghi chú |
|-----|-----------|------------|---------|
| 4.1 | Validate citation trước khi trả response | ⏳ | Check source tồn tại trong KB |
| 4.2 | Thêm groundedness check | ⏳ | So khớp citation với context |
| 4.3 | Cập nhật ChatService để reject nếu thiếu citation | ⏳ | |

### Ngày 5 — Monitoring & Telemetry (22/07)

| STT | Công việc | Trạng thái | Ghi chú |
|-----|-----------|------------|---------|
| 5.1 | Tạo AuditService (log ẩn danh) | ⏳ | |
| 5.2 | Thêm OpenTelemetry tracing | ⏳ | |
| 5.3 | Export Prometheus metrics | ⏳ | |
| 5.4 | Grafana dashboard mẫu | ⏳ | |

### Ngày 6 — Evaluation Suite (23/07)

| STT | Công việc | Trạng thái | Ghi chú |
|-----|-----------|------------|---------|
| 6.1 | Tạo 150 câu hỏi tiếng Việt | ⏳ | Chia: 70% dịch vụ, 20% BHYT, 10% khác |
| 6.2 | Tạo evaluation pipeline | ⏳ | |
| 6.3 | Đo Groundedness, Recall@20, Precision | ⏳ | |

### Ngày 7 — Document Expiry & Polish (24/07)

| STT | Công việc | Trạng thái | Ghi chú |
|-----|-----------|------------|---------|
| 7.1 | Expiry validation trong loader | ⏳ | |
| 7.2 | Content review workflow | ⏳ | |
| 7.3 | CI pipeline cho tests | ⏳ | |
| 7.4 | Final review & bug fixes | ⏳ | |

---

## 🎯 Key Metrics cho Phase 2

| Metric | Target | Hiện tại | Phase 2 Target |
|--------|--------|----------|----------------|
| **Retrieval Precision@5** | > 85% | ~75% | > 90% |
| **Groundedness** | 100% | ~95% | 100% |
| **Response time (p95)** | < 3s | ~2.5s | < 2s |
| **Citation rate** | 100% | ~90% | 100% |
| **Handoff accuracy** | > 95% | ~90% | > 95% |

---

## 🚧 Blockers & Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| ChromaDB dependency conflicts | Medium | Test trên venv riêng |
| Cross-encoder GPU requirement | High | Dùng CPU fallback, quantized model |
| 150 test questions quality | Medium | Nhờ domain expert review |
| Hybrid search latency | Low | Cache + async processing |

---

## 📂 File thay đổi trong Phase 2

```
ai-service/
├── rag/
│   ├── document_loader.py  → Thêm expiry check
│   ├── vector_store.py     → Refactor: FAISS → ChromaDB
│   ├── hybrid_retriever.py → NEW: Hybrid search
│   └── reranker.py         → NEW: Cross-encoder reranker
├── services/
│   ├── chat_service.py     → Thêm citation validation
│   ├── audit_service.py    → NEW: Audit logging
│   └── telemetry.py        → NEW: OpenTelemetry
├── metrics/
│   └── prometheus.py       → NEW: Metrics export
├── models/
│   └── schemas.py          → Thêm feedback fields
└── requirements.txt        → Thêm dependencies

knowledge/
└── approved/
    ├── gioi-thieu-benh-vien.md
    ├── dich-vu-kham-chua-benh.md
    └── lien-he-dat-lich.md

tests/
├── test_questions.json     → NEW: 150 câu hỏi
└── test_phase2_*.py        → NEW: Phase 2 tests

plans/
├── roadmap.md              → Tổng quan lộ trình
└── phase2-progress.md      → Theo dõi tiến độ
```
