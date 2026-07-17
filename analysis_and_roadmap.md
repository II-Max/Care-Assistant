# 🏥 AI Customer Care Assistant — Bệnh viện Tim Hà Nội
## Phân tích đề bài & Roadmap triển khai

---

## 1. Phân tích đề bài

### 1.1. Bối cảnh & Bài toán cốt lõi

| Yếu tố | Chi tiết |
|---|---|
| **Đơn vị** | Bệnh viện Tim Hà Nội — BV chuyên khoa hạng I, tuyến cuối về tim mạch |
| **Quy mô** | 2,500–3,000 bệnh nhân ngoại trú/ngày |
| **Pain point** | Lượng câu hỏi lặp lại lớn → quá tải tổng đài/lễ tân → phản hồi chậm, trải nghiệm không đồng nhất |
| **Giải pháp** | AI Chatbot tích hợp trực tiếp vào website bệnh viện |

### 1.2. Phân rã 6 yêu cầu chức năng

```mermaid
mindmap
  root((AI Customer Care<br/>Assistant))
    1. Knowledge QA
      Đặt lịch khám
      Quy trình khám chữa bệnh
      BHYT
      Bảng giá dịch vụ
      Giờ làm việc
      Bác sĩ & Khoa phòng
      Thông tin chính thống khác
    2. System Integration
      API lịch hẹn
      Redirect đặt lịch
      Truy vấn dịch vụ
    3. Conversational UX
      Text-based chat
      Bonus: ASR tiếng Việt
      Bonus: TTS tiếng Việt
    4. Trustworthy AI
      Grounded responses
      No hallucination
      Fallback to hotline
    5. Emergency Handling
      Phát hiện triệu chứng nguy hiểm
      Không đưa lời khuyên y tế
      Hướng dẫn cấp cứu ngay
    6. Deployment Ready
      Data privacy
      Information security
      Healthcare compliance
```

### 1.3. Phân loại mức độ ưu tiên

| Mức | Yêu cầu | Lý do |
|---|---|---|
| 🔴 **Must-have** | Knowledge QA, Trustworthy AI, Emergency Handling | Lõi sản phẩm — sai = rủi ro pháp lý & y tế |
| 🟡 **Should-have** | System Integration, Deployment Ready | Tạo giá trị thực tế, đáp ứng yêu cầu vận hành |
| 🟢 **Nice-to-have** | ASR/TTS tiếng Việt | Bonus điểm, nâng trải nghiệm cho người cao tuổi |

### 1.4. Các thách thức kỹ thuật then chốt

> [!CAUTION]
> **Rủi ro y tế**: Chatbot KHÔNG được phép chẩn đoán hay tư vấn điều trị. Mọi response phải grounded 100% từ knowledge base chính thống. Sai lệch có thể gây hậu quả nghiêm trọng.

| # | Thách thức | Giải pháp hướng đến |
|---|---|---|
| 1 | **Tiếng Việt y khoa** — thuật ngữ chuyên ngành, viết tắt, lỗi chính tả | Fine-tune embedding model cho medical Vietnamese; synonym mapping |
| 2 | **Hallucination control** — LLM có thể bịa thông tin | RAG + citation + confidence threshold + fallback |
| 3 | **Emergency detection** — nhận diện triệu chứng nguy hiểm | Rule-based keyword layer + LLM classification dual-check |
| 4 | **Data freshness** — bảng giá, lịch bác sĩ thay đổi thường xuyên | Automated sync pipeline từ HIS/API bệnh viện |
| 5 | **Privacy & Compliance** — dữ liệu y tế nhạy cảm | On-premise deployment, PII masking, audit logging |

---

## 2. Kiến trúc hệ thống đề xuất

### 2.1. High-level Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[Website Widget<br/>Chat UI] --> B[API Gateway]
        A2[Zalo Mini App] -.-> B
    end

    subgraph "Core AI Engine"
        B --> C[Orchestrator Service]
        C --> D[Emergency Detector]
        C --> E[Intent Classifier]
        E --> F[RAG Pipeline]
        E --> G[API Router]
        F --> H[(Vector DB<br/>Qdrant/Milvus)]
        F --> I[LLM Service<br/>GPT-4o / Gemini / <br/>Vietcuna Fine-tune]
        G --> J[Hospital API<br/>Gateway]
    end

    subgraph "Knowledge Layer"
        H --> K[(Document Store<br/>PostgreSQL)]
        K --> L[Admin CMS<br/>Knowledge Management]
    end

    subgraph "Hospital Systems"
        J --> M[HIS - Hospital<br/>Information System]
        J --> N[Appointment<br/>Booking API]
        J --> O[Service<br/>Catalog API]
    end

    subgraph "Bonus: Voice"
        P[ASR Service<br/>Whisper/Vietcuna] -.-> C
        C -.-> Q[TTS Service<br/>VITS/Zalo TTS]
    end

    subgraph "Observability"
        C --> R[Logging &<br/>Analytics]
        R --> S[Human Review<br/>Dashboard]
    end

    style D fill:#ff4444,color:#fff
    style A fill:#4CAF50,color:#fff
    style I fill:#2196F3,color:#fff
```

### 2.2. Luồng xử lý chính (Request Flow)

```mermaid
sequenceDiagram
    participant U as Bệnh nhân
    participant W as Chat Widget
    participant O as Orchestrator
    participant ED as Emergency Detector
    participant IC as Intent Classifier
    participant RAG as RAG Pipeline
    participant API as Hospital API
    participant LLM as LLM

    U->>W: "Tôi bị đau ngực dữ dội"
    W->>O: Send message
    O->>ED: Check emergency keywords

    alt 🚨 Emergency Detected
        ED-->>O: EMERGENCY FLAG
        O-->>W: ⚠️ Phản hồi cấp cứu ngay lập tức<br/>"Hãy gọi 115 hoặc đến Khoa Cấp cứu..."
        O-->>W: Hiển thị hotline + địa chỉ BV
    else Normal Query
        O->>IC: Classify intent
        IC-->>O: Intent: appointment_booking

        alt Needs Hospital Data
            O->>API: GET /schedules?doctor=...
            API-->>O: Schedule data
        end

        O->>RAG: Retrieve relevant docs
        RAG->>LLM: Context + Query + System Prompt
        LLM-->>RAG: Generated response (grounded)
        RAG-->>O: Response + citations
        O-->>W: Formatted answer + source links
    end

    W-->>U: Display response
```

### 2.3. Tech Stack đề xuất

| Layer | Công nghệ | Lý do chọn |
|---|---|---|
| **Frontend** | React / Next.js + Widget SDK | Dễ embed vào website hiện tại, responsive |
| **Backend** | Python FastAPI | Ecosystem ML/AI mạnh, async native |
| **LLM** | GPT-4o (primary) hoặc Gemini 2.5 Pro | Hiểu tiếng Việt tốt, reasoning mạnh |
| **Embedding** | `multilingual-e5-large` hoặc fine-tune `bge-m3` | Hỗ trợ tiếng Việt, chất lượng retrieval cao |
| **Vector DB** | Qdrant (self-hosted) | Open-source, dễ on-premise, performance tốt |
| **Document Store** | PostgreSQL + pgvector | Backup vector search + metadata storage |
| **Cache** | Redis | Session management, rate limiting |
| **Orchestration** | LangChain / LlamaIndex | RAG pipeline, tool-calling, memory |
| **ASR (bonus)** | OpenAI Whisper large-v3 | SOTA tiếng Việt, free, self-host được |
| **TTS (bonus)** | Zalo AI TTS / VITS fine-tune | Giọng Việt tự nhiên |
| **Monitoring** | Langfuse / LangSmith | LLM observability, tracing, evaluation |
| **Deployment** | Docker + K8s (on-premise) | Bảo mật dữ liệu y tế, compliance |

---

## 3. Roadmap triển khai

### 3.1. Tổng quan 4 Phase — 12 tuần

```mermaid
gantt
    title Roadmap triển khai — AI Customer Care Assistant
    dateFormat  YYYY-MM-DD
    axisFormat  %d/%m

    section Phase 1: Foundation
    Thu thập & xử lý Knowledge Base     :p1a, 2026-07-21, 7d
    Xây dựng RAG Pipeline cơ bản        :p1b, 2026-07-21, 10d
    Emergency Detection Module           :p1c, 2026-07-25, 5d
    Trustworthy AI guardrails            :p1d, 2026-07-28, 5d
    Unit tests & evaluation              :p1e, 2026-08-01, 3d

    section Phase 2: Integration & UX
    Chat Widget Frontend                 :p2a, 2026-08-04, 7d
    Hospital API Integration             :p2b, 2026-08-04, 10d
    Conversation Memory & Context        :p2c, 2026-08-11, 5d
    Multi-turn dialogue handling         :p2d, 2026-08-14, 4d

    section Phase 3: Polish & Voice
    Response quality tuning              :p3a, 2026-08-18, 5d
    Admin CMS cho Knowledge Base         :p3b, 2026-08-18, 7d
    ASR tiếng Việt (bonus)               :p3c, 2026-08-25, 5d
    TTS tiếng Việt (bonus)               :p3d, 2026-08-25, 5d
    Analytics Dashboard                  :p3e, 2026-08-28, 4d

    section Phase 4: Deploy & Launch
    Security audit & penetration test    :p4a, 2026-09-01, 5d
    On-premise deployment setup          :p4b, 2026-09-01, 5d
    UAT với staff bệnh viện             :p4c, 2026-09-08, 5d
    Soft launch (10% traffic)            :p4d, 2026-09-13, 3d
    Full launch + monitoring             :p4e, 2026-09-16, 5d
```

### 3.2. Chi tiết từng Phase

---

#### 📦 Phase 1: Foundation (Tuần 1–3)
> *Mục tiêu: RAG pipeline hoạt động chính xác, phát hiện cấp cứu, không hallucinate*

| Task | Deliverable | Acceptance Criteria |
|---|---|---|
| **1.1 Thu thập Knowledge Base** | Bộ tài liệu chuẩn hóa (Markdown/JSON) | Cover ≥ 95% FAQ từ tổng đài |
| **1.2 Chunking & Embedding** | Vector DB với toàn bộ knowledge | Retrieval accuracy ≥ 90% trên test set |
| **1.3 RAG Pipeline** | API endpoint trả lời câu hỏi | Grounded answer rate ≥ 95% |
| **1.4 Emergency Detector** | Module phát hiện cấp cứu | Recall ≥ 99% (không miss emergency) |
| **1.5 Guardrails** | Hệ thống chặn hallucination | 0% fabricated medical advice |
| **1.6 Evaluation Framework** | Bộ test tự động + metrics | RAGAS score ≥ 0.85 |

**Chi tiết kỹ thuật Phase 1:**

```
📂 Knowledge Base Structure
├── 📄 appointment/
│   ├── booking_process.md
│   ├── online_booking_guide.md
│   └── follow_up_appointments.md
├── 📄 departments/
│   ├── cardiology.md
│   ├── cardiac_surgery.md
│   ├── pediatric_cardiology.md
│   └── ...
├── 📄 doctors/
│   └── doctor_profiles.json
├── 📄 insurance/
│   ├── bhyt_coverage.md
│   ├── required_documents.md
│   └── reimbursement_process.md
├── 📄 services/
│   ├── service_catalog.json
│   ├── pricing.json
│   └── working_hours.md
├── 📄 procedures/
│   ├── admission.md
│   ├── examination_flow.md
│   └── discharge.md
└── 📄 emergency/
    ├── emergency_symptoms.json
    └── emergency_procedures.md
```

**Emergency Detection — Dual-layer approach:**

```python
# Layer 1: Rule-based keyword detection (fast, high recall)
EMERGENCY_KEYWORDS = [
    "đau ngực dữ dội", "khó thở", "ngất xỉu", "bất tỉnh",
    "đau tim", "tức ngực", "tim đập nhanh bất thường",
    "mất ý thức", "co giật", "tím tái", "ngừng thở",
    "chest pain", "shortness of breath", "fainting"
]

# Layer 2: LLM classification (accurate, contextual)
EMERGENCY_SYSTEM_PROMPT = """
Bạn là bộ phân loại cấp cứu y tế. Đánh giá tin nhắn của bệnh nhân:
- EMERGENCY: Triệu chứng nguy hiểm cần cấp cứu ngay
- URGENT: Cần khám sớm nhưng chưa cấp cứu
- NORMAL: Câu hỏi thông tin thông thường
CHỈ trả về 1 từ: EMERGENCY, URGENT, hoặc NORMAL.
"""
```

---

#### 🔗 Phase 2: Integration & UX (Tuần 3–5)
> *Mục tiêu: Chat widget đẹp, tích hợp API bệnh viện, hội thoại đa lượt mượt mà*

| Task | Deliverable | Acceptance Criteria |
|---|---|---|
| **2.1 Chat Widget** | Floating widget embed vào website | Responsive, load < 2s, accessible |
| **2.2 Hospital API** | Connector tới HIS/Booking | Lấy được lịch hẹn, dịch vụ real-time |
| **2.3 Conversation Memory** | Multi-turn context management | Nhớ context trong phiên chat |
| **2.4 Intent Router** | Phân loại intent → route action | Accuracy ≥ 92% trên test intents |

**Intent Classification Schema:**

| Intent | Action | Example |
|---|---|---|
| `appointment.book` | Redirect → Booking page/Zalo | "Tôi muốn đặt lịch khám" |
| `appointment.check` | API call → Schedule lookup | "Bác sĩ A có lịch ngày nào?" |
| `insurance.coverage` | RAG → Knowledge Base | "BHYT chi trả những gì?" |
| `service.pricing` | RAG + API → Pricing data | "Siêu âm tim giá bao nhiêu?" |
| `doctor.info` | RAG → Doctor profiles | "Bác sĩ nào giỏi nhất về van tim?" |
| `procedure.guide` | RAG → Procedure docs | "Nhập viện cần giấy tờ gì?" |
| `emergency` | Hard-coded response | "Tôi đang đau ngực dữ dội" |
| `greeting` | Template response | "Xin chào" |
| `out_of_scope` | Polite decline + redirect | "Cho tôi hỏi về bệnh dạ dày" |

---

#### ✨ Phase 3: Polish & Voice (Tuần 5–8)
> *Mục tiêu: Nâng chất lượng response, thêm voice, dashboard quản trị*

| Task | Deliverable | Acceptance Criteria |
|---|---|---|
| **3.1 Response Tuning** | Prompt engineering + few-shot | User satisfaction ≥ 4.2/5 |
| **3.2 Admin CMS** | Web app quản lý Knowledge Base | CRUD documents, preview changes |
| **3.3 ASR (bonus)** | Speech-to-text tiếng Việt | WER < 15% trên medical terms |
| **3.4 TTS (bonus)** | Text-to-speech giọng Việt | MOS ≥ 3.8, latency < 3s |
| **3.5 Analytics** | Dashboard thống kê | Realtime metrics, conversation logs |

**Analytics Metrics:**

| Metric | Mô tả | Target |
|---|---|---|
| Response Accuracy | % câu trả lời chính xác (human eval) | ≥ 95% |
| Fallback Rate | % câu hỏi bot không trả lời được | ≤ 10% |
| Avg Response Time | Thời gian phản hồi trung bình | < 3s |
| Emergency Detection Rate | % emergency phát hiện đúng | ≥ 99% |
| User Satisfaction (CSAT) | Đánh giá từ bệnh nhân | ≥ 4.2/5 |
| Conversation Completion | % hội thoại giải quyết xong | ≥ 80% |
| Daily Active Conversations | Số phiên chat/ngày | Tracking |

---

#### 🚀 Phase 4: Deploy & Launch (Tuần 8–12)
> *Mục tiêu: Triển khai an toàn, tuân thủ bảo mật, vận hành ổn định*

| Task | Deliverable | Acceptance Criteria |
|---|---|---|
| **4.1 Security Audit** | Báo cáo bảo mật | Pass penetration test |
| **4.2 On-premise Deploy** | Hệ thống chạy trên infra BV | 99.5% uptime |
| **4.3 UAT** | User Acceptance Testing | Staff BV approve |
| **4.4 Soft Launch** | 10% traffic thử nghiệm | No critical bugs |
| **4.5 Full Launch** | 100% traffic + monitoring | Stable 48h |

**Deployment Architecture (On-premise):**

```mermaid
graph LR
    subgraph "DMZ"
        LB[Load Balancer<br/>Nginx]
    end

    subgraph "Application Zone"
        LB --> APP1[App Server 1<br/>FastAPI]
        LB --> APP2[App Server 2<br/>FastAPI]
        APP1 --> REDIS[Redis<br/>Session/Cache]
        APP2 --> REDIS
    end

    subgraph "AI Zone"
        APP1 --> LLM_GW[LLM Gateway<br/>Rate Limiter]
        APP2 --> LLM_GW
        LLM_GW --> VDB[Qdrant<br/>Vector DB]
        LLM_GW -->|HTTPS| EXT_LLM[External LLM API<br/>GPT-4o / Gemini]
    end

    subgraph "Data Zone"
        VDB --> PG[(PostgreSQL<br/>Knowledge + Logs)]
    end

    subgraph "Hospital Network"
        APP1 --> HIS[HIS System]
        APP2 --> HIS
    end

    style LB fill:#FF9800,color:#fff
    style EXT_LLM fill:#9C27B0,color:#fff
    style HIS fill:#4CAF50,color:#fff
```

---

## 4. Chiến lược Trustworthy AI

> [!IMPORTANT]
> Đây là yếu tố QUAN TRỌNG NHẤT của dự án. Chatbot y tế sai thông tin có thể gây hậu quả nghiêm trọng.

### 4.1. Multi-layer Safety Architecture

```mermaid
graph TD
    A[User Input] --> B{Layer 1:<br/>Emergency Detection}
    B -->|🚨 Emergency| C[Hard-coded Emergency Response<br/>Gọi 115 / Đến Cấp cứu]
    B -->|Safe| D{Layer 2:<br/>Input Validation}
    D -->|Out of scope| E[Polite Decline<br/>+ Redirect to Hotline]
    D -->|Valid| F[Layer 3:<br/>RAG Retrieval]
    F --> G{Layer 4:<br/>Confidence Check}
    G -->|Low confidence<br/>< 0.7| H[Acknowledge Uncertainty<br/>+ Redirect to Staff]
    G -->|High confidence| I[Layer 5:<br/>LLM Generation<br/>with Strict Prompt]
    I --> J{Layer 6:<br/>Output Guardrail}
    J -->|Contains medical advice<br/>or ungrounded claims| K[Block & Fallback]
    J -->|Clean| L[✅ Deliver Response<br/>with Source Citations]

    style C fill:#ff4444,color:#fff
    style K fill:#ff4444,color:#fff
    style L fill:#4CAF50,color:#fff
```

### 4.2. System Prompt Strategy

```text
Bạn là trợ lý chăm sóc khách hàng của Bệnh viện Tim Hà Nội.

QUY TẮC BẮT BUỘC:
1. CHỈ trả lời dựa trên thông tin trong [CONTEXT] được cung cấp.
2. KHÔNG BAO GIỜ tự bịa thông tin về giá dịch vụ, lịch bác sĩ, hay quy trình.
3. KHÔNG đưa lời khuyên y tế, chẩn đoán bệnh, hay gợi ý thuốc.
4. Nếu không có đủ thông tin, nói rõ: "Xin lỗi, tôi chưa có thông tin này.
   Quý khách vui lòng liên hệ Tổng đài 1900-xxxx để được hỗ trợ."
5. Luôn ghi nguồn thông tin cuối câu trả lời.
6. Phản hồi lịch sự, chuyên nghiệp, dễ hiểu.
7. Nếu phát hiện triệu chứng nguy hiểm → NGAY LẬP TỨC hướng dẫn cấp cứu.
```

---

## 5. Compliance & Data Privacy

| Yêu cầu | Giải pháp |
|---|---|
| **PII Protection** | Không lưu trữ CMND/CCCD, SĐT trong conversation logs; masking tự động |
| **Data Residency** | On-premise deployment, dữ liệu không rời khỏi infra BV |
| **Audit Trail** | Log toàn bộ conversation (anonymized) cho review |
| **Access Control** | RBAC cho Admin CMS, API key rotation |
| **Encryption** | TLS 1.3 in-transit, AES-256 at-rest |
| **Nghị định 13/2023/NĐ-CP** | Tuân thủ quy định bảo vệ dữ liệu cá nhân Việt Nam |
| **Thông tư 46/2018/TT-BYT** | Tuân thủ quy định về CNTT trong y tế |

---

## 6. Đội ngũ đề xuất

| Vai trò | Số lượng | Trách nhiệm |
|---|---|---|
| **Tech Lead / AI Engineer** | 1 | Kiến trúc hệ thống, RAG pipeline, LLM integration |
| **Backend Developer** | 1–2 | API, Hospital integration, deployment |
| **Frontend Developer** | 1 | Chat widget, Admin CMS |
| **Domain Expert (BV)** | 1 | Cung cấp & validate knowledge base |
| **QA / Tester** | 1 | Test scenarios, evaluation, UAT |

---

## 7. Rủi ro & Mitigation

| # | Rủi ro | Mức độ | Mitigation |
|---|---|---|---|
| 1 | LLM hallucinate thông tin y tế | 🔴 Cao | Multi-layer guardrails + human review |
| 2 | API bệnh viện không sẵn sàng / thiếu tài liệu | 🟡 TB | Mock API → graceful degradation |
| 3 | Knowledge base không đầy đủ | 🟡 TB | Iterative update + admin CMS |
| 4 | Latency cao khi gọi LLM API | 🟡 TB | Caching, streaming response, fallback model |
| 5 | Bệnh nhân lớn tuổi không quen chatbot | 🟢 Thấp | UI đơn giản + voice option (bonus) |
| 6 | Chi phí LLM API cao với 3000 user/ngày | 🟡 TB | Smart caching, smaller model cho FAQ đơn giản |

---

## 8. Ước tính chi phí vận hành (hàng tháng)

| Hạng mục | Ước tính | Ghi chú |
|---|---|---|
| **LLM API** (GPT-4o) | $500–1,500/tháng | ~3000 conversations/ngày, avg 5 turns |
| **Infrastructure** (on-premise) | Tận dụng infra BV | GPU server nếu self-host LLM |
| **Vector DB + PostgreSQL** | $0 (open-source) | Self-hosted Qdrant |
| **Monitoring** (Langfuse) | $0–200/tháng | Open-source hoặc cloud |
| **Maintenance** | 1 engineer part-time | Knowledge update, model tuning |

> [!TIP]
> **Tối ưu chi phí**: Có thể dùng model nhỏ hơn (GPT-4o-mini, Gemini Flash) cho các câu hỏi FAQ đơn giản, chỉ dùng model lớn cho câu hỏi phức tạp → giảm ~60% chi phí LLM.

---

## 9. KPIs đo lường thành công

| KPI | Target Phase 1 | Target 3 tháng | Target 6 tháng |
|---|---|---|---|
| **Response Accuracy** | ≥ 90% | ≥ 95% | ≥ 97% |
| **Emergency Detection Recall** | ≥ 99% | ≥ 99.5% | ≥ 99.9% |
| **Hallucination Rate** | ≤ 5% | ≤ 2% | ≤ 1% |
| **Avg Response Time** | < 5s | < 3s | < 2s |
| **User Satisfaction (CSAT)** | ≥ 3.8/5 | ≥ 4.2/5 | ≥ 4.5/5 |
| **Hotline Call Reduction** | 10% | 25% | 40% |
| **Self-service Resolution Rate** | ≥ 60% | ≥ 75% | ≥ 85% |

---

## 10. Tổng kết

Dự án AI Customer Care Assistant cho Bệnh viện Tim Hà Nội là bài toán **RAG-based conversational AI** trong domain **healthcare** — đòi hỏi sự cân bằng giữa **trải nghiệm người dùng** và **an toàn y tế tuyệt đối**.

**3 trụ cột thành công:**

1. **🎯 Accuracy** — Knowledge base đầy đủ + RAG pipeline chất lượng
2. **🛡️ Safety** — Multi-layer guardrails + emergency detection + no hallucination
3. **💬 Experience** — UI thân thiện + phản hồi nhanh + voice support

> [!NOTE]
> Roadmap 12 tuần trên đây là baseline. Tùy vào mức độ sẵn sàng của API bệnh viện và chất lượng knowledge base ban đầu, timeline có thể điều chỉnh ± 2 tuần.
