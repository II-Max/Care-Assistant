# 📋 Hospital Website — Kiến Trúc Hệ Thống & Prompt Chuyên Nghiệp

---
## Bài Toán :
1. Tóm tắt bối cảnh và thách thức (Background & Challenge)
Bối cảnh: Bệnh viện Tim Hà Nội là bệnh viện chuyên khoa tim mạch hạng I, tiếp nhận khoảng 2.500 - 3.000 bệnh nhân ngoại trú mỗi ngày. Lượng câu hỏi lặp đi lặp lại về thủ tục, lịch khám, giá dịch vụ, bảo hiểm y tế... qua các kênh truyền thống đang gây áp lực lớn cho nhân viên y tế, dẫn đến phản hồi chậm và trải nghiệm khách hàng chưa đồng bộ.12
Thách thức: Phát triển một Trợ lý Chăm sóc Khách hàng AI (AI Customer Care Assistant) tích hợp trực tiếp vào website của bệnh viện để hỗ trợ giải đáp thắc mắc và cung cấp thông tin cho bệnh nhân cùng người nhà.3
2. Bài toán chính (Cô đọng)
Bài toán: Thiết kế và triển khai một hệ thống Trợ lý AI giải đáp thông tin y tế và dịch vụ dựa trên bộ tri thức chính thống của Bệnh viện Tim Hà Nội, có khả năng kết nối hệ thống dữ liệu và đảm bảo an toàn thông tin, nhằm giảm tải cho đội ngũ nhân sự và tối ưu hóa trải nghiệm của người bệnh.4562
3. Các tiêu chí cốt lõi cần đáp ứng
Trả lời dựa trên tri thức (Knowledge-based QA): Phản hồi chính xác các thông tin về đặt lịch, quy trình khám chữa bệnh, bảo hiểm y tế (BHYT), giá dịch vụ, giờ làm việc và thông tin các khoa phòng/bác sĩ.7
Tích hợp hệ thống (System Integration): Có khả năng kết nối với API hoặc hệ thống thông tin của bệnh viện để tra cứu lịch hẹn, thông tin dịch vụ và điều hướng người dùng đến các kênh đặt lịch (Website, Zalo Mini App, Hotline).8
Trải nghiệm hội thoại (Conversational Experience): Hỗ trợ giao tiếp qua văn bản (Text-based). Điểm cộng lớn nếu tích hợp thêm công nghệ nhận dạng giọng nói (ASR) và tổng hợp giọng nói (TTS) bằng tiếng Việt.910
Trí tuệ nhân tạo đáng tin cậy (Trustworthy AI): Câu trả lời phải dựa hoàn toàn trên cơ sở dữ liệu chính thức của bệnh viện, tuyệt đối không tự tạo lập thông tin (hallucinate). Nếu thiếu thông tin, phải hướng dẫn người dùng đến các kênh hỗ trợ phù hợp.11
Xử lý tình huống khẩn cấp (Emergency Handling): Khi phát hiện các triệu chứng khẩn cấp (đau ngực dữ dội, khó thở, ngất xỉu...), AI tuyệt đối không đưa ra lời khuyên điều trị mà phải lập tức hướng dẫn người dùng tiếp cận dịch vụ cấp cứu hoặc đến khoa Cấp cứu của bệnh viện.12
Sẵn sàng triển khai (Deployment Readiness): Khả năng cài đặt trên hạ tầng của bệnh viện và tuân thủ nghiêm ngặt các quy định về bảo mật dữ liệu, quyền riêng tư và bảo vệ dữ liệu y tế.6
## PHẦN 1: TOÀN BỘ CẤU TRÚC HỆ THỐNG Gợi Ý

### 1.1 Cây Thư Mục Dự Án

```
NEO-ONLINE-JUDGE-main/  (repo: github.com/II-Max/GTS)
│
├── 📁 backend/                          # Python Backend (Flask + Judge Engine)
│   ├── __init__.py                      # Package marker
│   ├── app.py                           # ⭐ Entry point chính — Flask app + Polling loop
│   │
│   ├── 📁 config/
│   │   ├── settings.py                  # ⭐ Centralized config — đọc .env, quản lý toàn bộ biến
│   │   └── logging.py                   # Structured logging (JSON + rotating file)
│   │
│   ├── 📁 core/
│   │   ├── __init__.py
│   │   ├── compiler.py                  # Multi-language compiler (Python/C++/C/Java/JS/Pascal)
│   │   └── judge.py                     # Grading engine — chạy code vs test cases
│   │
│   ├── 📁 models/
│   │   ├── __init__.py
│   │   └── submission.py                # Dataclass: Submission, Problem, AIRequest, GradingResult
│   │
│   ├── 📁 routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py               # ⭐ REST API: /api/auth/* (login, register, profile, admin)
│   │   └── playground_routes.py         # REST API: /api/playground/* (run code, AI chat)
│   │
│   ├── 📁 services/
│   │   ├── __init__.py
│   │   ├── ai_service.py                # ⭐ AI Mentor — gọi NVIDIA NIM / OpenAI
│   │   ├── auth_service.py              # ⭐ Auth logic: Firebase Auth + JWT + OAuth sync
│   │   └── firebase_service.py          # ⭐ Firebase RTDB CRUD (Singleton pattern)
│   │
│   └── 📁 scripts/
│       └── ai_agent_cli.py              # CLI tool test AI
│
├── 📁 frontend/                         # Static HTML/CSS/JS (Firebase Hosting)
│   ├── index.html                       # Landing page
│   ├── login.html                       # Đăng nhập/Đăng ký
│   ├── problems.html                    # Danh sách bài tập
│   ├── solve.html                       # IDE nộp bài
│   ├── playground.html                  # Code playground + AI chat
│   ├── contest.html                     # Phòng thi
│   ├── contest_room.html               # Bên trong phòng thi
│   ├── rank.html                        # Bảng xếp hạng
│   ├── history.html                     # Lịch sử làm bài
│   ├── documents.html                   # Tài liệu học tập
│   ├── videos.html                      # Video bài giảng
│   ├── about.html                       # Giới thiệu
│   ├── guide.html                       # Hướng dẫn sử dụng
│   ├── essay.html                       # Bài luận
│   ├── 404.html                         # Error page
│   ├── test-local-ai.html               # Test AI local
│   │
│   ├── 📁 css/
│   │   └── neo-design.css               # ⭐ Design system (17KB — cyberpunk/neon theme)
│   │
│   └── 📁 js/
│       ├── firebase-config.js           # ⭐ Firebase SDK init + API_BASE + utility functions
│       └── firebase-auth-check.js       # ⭐ Auth guard + dynamic navbar injection
│
├── 📁 setup/                            # DevOps & Deployment
│   ├── Dockerfile                       # Docker image cho judge
│   ├── docker-compose.yml               # Compose: judge + redis + firebase-emulator
│   ├── 📁 scripts/                      # Setup scripts
│   └── setup_system.py                  # System provisioning script (23KB)
│
├── 📁 tests/
│   └── __init__.py
│
├── 📁 logs/                             # Runtime logs (gitignored)
│
├── 📄 Cấu hình gốc
│   ├── .env                             # 🔒 Biến môi trường (NVIDIA API, Firebase, JWT...)
│   ├── .env.example                     # Template .env
│   ├── firebase.json                    # Firebase CLI config (hosting + database rules)
│   ├── .firebaserc                      # Firebase project binding (gtsv2-a93c5)
│   ├── database.rules.json             # ⭐ Firebase RTDB Security Rules v3.0
│   ├── service-account.json            # 🔒 Firebase Admin SDK credential
│   ├── requirements.txt                # Python deps (flask, firebase-admin, pyjwt, redis...)
│   ├── Dockerfile                       # Root Dockerfile
│   └── .gitignore                       # Comprehensive gitignore
│
├── 📄 Tài liệu
│   ├── README.md                        # Tài liệu chính (14KB)
│   ├── DataBase.md                      # Cấu trúc CSDL chi tiết (10KB)
│   ├── VẬN_HÀNH.md                     # Hướng dẫn vận hành (19KB)
│   ├── V2Update.md                      # Changelog v2
│   └── GTS_Project_Introduction.tex     # LaTeX intro
│
└── 📄 Utility Scripts
    ├── fix_avatars.py
    ├── rebrand.py
    ├── sync_leaderboard.py
    └── test_nvidia.py
```

---

### 1.2 Công Nghệ Sử Dụng

| Layer | Công nghệ | Chi tiết |
|-------|-----------|----------|
| **Backend Runtime** | Python 3.10+ | Flask 3.0+, async-compatible |
| **Web Framework** | Flask + Flask-CORS | RESTful API, blueprint-based routing |
| **Authentication** | Firebase Auth + PyJWT | Google/GitHub OAuth, Email/Password, JWT sessions |
| **Database** | Firebase Realtime Database | NoSQL JSON tree, Admin SDK (server-side) |
| **AI Service** | NVIDIA NIM API (primary) | Model: `meta/llama-3.1-70b-instruct`, fallback OpenAI |
| **Judge Engine** | Custom (subprocess-based) | Python, C++, C, Java, JavaScript, Pascal |
| **Frontend** | Vanilla HTML/CSS/JS | Static SPA, Firebase JS SDK v9-compat |
| **Hosting** | Firebase Hosting | Static file serving |
| **CSS Theme** | Custom `neo-design.css` | Cyberpunk/Neon glassmorphism design (17KB) |
| **Logging** | python-json-logger | JSON structured logs, rotating file handlers |
| **Queue (Optional)** | Redis + RQ | For scaling judge workers |
| **Containerization** | Docker + Docker Compose | Multi-service deployment |
| **Security** | Firebase RTDB Rules v3.0 | Role-based (student/teacher), validate on write |
| **CORS** | Whitelist-based | Production domains + localhost |

---

### 1.3 Kiến Trúc Hiện Tại (Sơ Đồ)

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND                                │
│  (Firebase Hosting — Static HTML/CSS/JS)                     │
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐   │
│  │ Login    │ │ Problems │ │ Solve    │ │ Playground    │   │
│  │ Register │ │ List     │ │ (IDE)    │ │ (Run+AI Chat) │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬────────┘   │
│       │             │            │               │            │
│       └─────────────┼────────────┼───────────────┘            │
│                     │            │                             │
│     Firebase JS SDK │    REST API│ (Bearer Token)              │
│     (Auth + RTDB)   │            │                             │
└─────────────────────┼────────────┼─────────────────────────────┘
                      │            │
                      │            │ HTTP/S
                      ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (Python/Flask)                     │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────────────────────┐  │
│  │ Flask API Server │  │ Main Polling Loop                │  │
│  │ (Thread)         │  │ (Main Thread)                    │  │
│  │                  │  │                                  │  │
│  │ /api/auth/*      │  │ 1. Process AI Requests           │  │
│  │ /api/playground/*│  │ 2. Process Practice Submissions  │  │
│  │ /api/health      │  │ 3. Process Contest Submissions   │  │
│  │ /api/stats       │  │ → Sleep(POLL_INTERVAL) → Loop    │  │
│  └────────┬─────────┘  └────────────┬─────────────────────┘  │
│           │                          │                        │
│  ┌────────┴──────────────────────────┴─────────────────────┐  │
│  │                    SERVICES LAYER                       │  │
│  │  ┌─────────────┐ ┌──────────────┐ ┌──────────────────┐  │  │
│  │  │AuthService  │ │FirebaseService│ │AIService         │  │  │
│  │  │(JWT+OAuth)  │ │(RTDB CRUD)   │ │(NVIDIA/OpenAI)   │  │  │
│  │  └─────────────┘ └──────────────┘ └──────────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    CORE LAYER                           │  │
│  │  ┌──────────────┐  ┌─────────────────────────────────┐  │  │
│  │  │ Compiler     │  │ JudgeEngine                     │  │  │
│  │  │ (6 languages)│  │ (Grade test cases, scoring)     │  │  │
│  │  └──────────────┘  └─────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬───────────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │  Firebase RTDB      │
                    │  (Admin SDK)        │
                    │                     │
                    │  ├── users/         │
                    │  ├── problems/      │
                    │  ├── submissions/   │
                    │  ├── ai_requests/   │
                    │  ├── contests/      │
                    │  ├── public_leader… │
                    │  ├── global_chat/   │
                    │  ├── documents/     │
                    │  └── videos/        │
                    └─────────────────────┘
```

---

### 1.4 Các Endpoint API Hiện Tại

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| POST | `/api/auth/register` | ❌ | Đăng ký tài khoản (email/password) |
| POST | `/api/auth/login` | ❌ | Đăng nhập (Firebase ID Token) |
| GET | `/api/auth/profile` | 🔒 | Lấy profile user |
| PUT | `/api/auth/profile` | 🔒 | Cập nhật profile (display_name, avatar) |
| POST | `/api/auth/sync` | ❌ | Đồng bộ OAuth user |
| GET | `/api/auth/rank` | 🔒 | Bảng xếp hạng |
| GET | `/api/auth/admin/users` | 🔒👑 | [Admin] Danh sách users |
| PUT | `/api/auth/admin/users/<uid>` | 🔒👑 | [Admin] Cập nhật user |
| POST | `/api/playground/run` | 🔒 | Chạy code (rate-limited) |
| POST | `/api/playground/ai-chat` | 🔒 | Chat với AI |
| GET | `/api/health` | ❌ | Health check |
| GET | `/api/stats` | ❌ | Platform stats |

---

### 1.5 Firebase RTDB Security Rules v3.0 — Tóm Tắt

| Node | Read | Write | Validation |
|------|------|-------|------------|
| `users/{uid}` | Owner + Teacher | Owner (trừ role/score) + Teacher | Role chỉ được set `student` lần đầu |
| `public_leaderboard` | Public | **Backend only** (Admin SDK) | — |
| `problems` | Public | Teacher only | — |
| `submissions/$id` | Owner + Teacher | Create-only (no update) | `uid === auth.uid && status === 'pending'` |
| `contest_submissions` | Owner + Teacher | Create-only | Same as submissions |
| `ai_requests/$id` | Owner + Teacher | Create-only | `uid === auth.uid && status === 'pending'` |
| `global_chat/$id` | Authenticated | Create-only + validate | `name === display_name && role === user.role` |
| `documents`, `videos` | Authenticated | Teacher only | — |
| `contests` | Authenticated | Teacher only | — |

---

---

## PHẦN 2: PROMPT CHUYÊN NGHIỆP — CHUYỂN ĐỔI SANG WEBSITE BỆNH VIỆN


```markdown
# 🏥 PROMPT CHUYỂN ĐỔI: GTS Online Judge → Website Bệnh Viện Thông Minh

## BỐI CẢNH DỰ ÁN

Thực hiện tạo ra một website bệnh viên có tích hợp trí tuệ nhân tạo.

### Stack Công Nghệ
| Layer | Công nghệ | Ghi chú |
|-------|-----------|---------|
| Backend | **Python 3.10+ / Flask 3.0+** | RESTful API, blueprint routing |
| Database | **Firebase Realtime Database** | NoSQL JSON tree, Admin SDK (server) |
| Auth | **Firebase Authentication + PyJWT** | Google/GitHub OAuth, Email/Password |
| Frontend | **Vanilla HTML / CSS / JavaScript** | Static SPA, Firebase JS SDK |
| Hosting | **Firebase Hosting** | Static file serving |
| AI | **FastAPI** (MỚI — thay Flask cho AI service) | Chạy riêng, kết nối NVIDIA NIM API |
| CSS | **Custom Design System** (`neo-design.css`) | Sẽ redesign cho y tế |
| Logging | **python-json-logger** | JSON structured, rotating files |
| Container | **Docker + Docker Compose** | Multi-service |
| Security | **Firebase RTDB Rules** | Role-based, validate-on-write |
- Hãy nâng cấp và thay đổi phù hợp đối với mục tiêu
### Cấu Trúc Gợi Ý
```
project-root/
├── backend/
│   ├── app.py              # Flask entry point + polling loop
│   ├── config/             # settings.py (env vars), logging.py
│   ├── core/               # compiler.py, judge.py (sẽ xóa/thay)
│   ├── models/             # submission.py (sẽ refactor)
│   ├── routes/             # auth_routes.py, playground_routes.py
│   ├── services/           # ai_service.py, auth_service.py, firebase_service.py
│   └── scripts/            # CLI tools
├── frontend/               # Static HTML/CSS/JS pages
│   ├── css/neo-design.css
│   ├── js/firebase-config.js, firebase-auth-check.js
│   └── *.html
├── setup/                  # Docker, docker-compose, setup scripts
├── database.rules.json     # Firebase Security Rules
├── firebase.json           # Firebase CLI config
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
└── service-account.json    # Firebase Admin SDK credential
```

---

## YÊU CẦU CHUYỂN ĐỔI TỔNG THỂ

Chuyển đổi **toàn bộ hệ thống** từ Online Judge sang **Website Bệnh Viện Thông Minh** với các
nguyên tắc sau:

### 🎯 1. MỤC TIÊU CHÍNH
- **Ứng dụng** hạ tầng: Flask framework, Firebase Auth, Firebase RTDB,
  JWT system, CORS config, logging, Docker, deployment pipeline.
- **Xây ** toàn bộ frontend theo hướng y tế/bệnh viện với giao diện chuyên nghiệp, hiện đại.
- **Xây ** AI Service trên **FastAPI** (tách riêng khỏi Flask) với **RAG bắt buộc**.

---

### 🤖 2. AI SERVICE — FastAPI + RAG (BẮT BUỘC)

> **CRITICAL: AI Service PHẢI sử dụng kiến trúc RAG (Retrieval-Augmented Generation).**

#### 2.1 Kiến Trúc AI Service

```
ai-service/                     # Microservice riêng, chạy trên port khác (ví dụ: 8001)
├── main.py                     # FastAPI entry point
├── config.py                   # Settings (NVIDIA API key, model, RAG config...)
├── rag/
│   ├── __init__.py
│   ├── document_loader.py      # Load & parse tệp Markdown dataset
│   ├── chunker.py              # Chia document thành chunks (semantic chunking)
│   ├── embedder.py             # Tạo embeddings (dùng model embedding local hoặc API)
│   ├── vector_store.py         # Vector store (FAISS / ChromaDB / in-memory)
│   └── retriever.py            # Tìm kiếm chunks liên quan từ query
├── services/
│   ├── chat_service.py         # Xử lý chat: retrieve → augment prompt → call LLM
│   └── health_advisor.py       # Logic tư vấn sức khỏe
├── data/
│   └── medical_knowledge.md    # ⭐ TỆP DỮ LIỆU MARKDOWN DUY NHẤT (do team cung cấp)
├── models/
│   └── schemas.py              # Pydantic models cho request/response
├── requirements.txt            # fastapi, uvicorn, faiss-cpu, sentence-transformers...
└── Dockerfile                  # Container riêng cho AI service
```

#### 2.2 Nguyên Tắc RAG Tuyệt Đối

1. **NGUỒN DỮ LIỆU DUY NHẤT:** AI chỉ được phép đọc và suy luận từ tệp hoặc 1 folder
   `data/medical_knowledge.md` — một/ nhiều file Markdown lớn do team cung cấp hãy lựa chọn phương án đọc 1 hoặc nhiều (1 file sẽ là 1 file markdown lớn và nhiều file sẽ được tách biệt và đặt tên dựa theo dữ liệu).
2. **CẤM hoàn toàn:** Không được gọi API bên ngoài để lấy thông tin y tế (không Google,
   không Wikipedia, không PubMed). Mọi câu trả lời PHẢI dựa trên nội dung trong dataset.
3. **Luồng xử lý RAG:**
   ```
   User Query → Embedding → Vector Search (trong dataset) → Top-K chunks
        → Augmented Prompt (system + retrieved context + user question)
        → LLM (NVIDIA NIM API) → Response
   ```
4. **Khi startup:** FastAPI app phải:
   - Load file/ các file ví dụ : `medical_knowledge.md`
   - Chunk thành các đoạn nhỏ (500-1000 tokens, overlap 100 tokens) hãy lựa chọn thông số cho phù hợp đối với một ứng dụng Chat Bot dành cho y tế
   - Tạo embeddings cho từng chunk hãy lựa chọn mô hình embed phù hợp
   - Lưu vào vector store (FAISS hoặc ChromaDB) hãy lựa chọn công nghệ phù hợp
5. **Khi nhận query:**
   - Embed query → search top-K chunks gần nhất hãy lựa chọn K phù hợp
   - Nếu không tìm thấy context liên quan (similarity < threshold): trả lời
     "Xin lỗi, thông tin này nằm ngoài phạm vi dữ liệu của chúng tôi." hoặc lựa chọn phương án Get API tới một Module chat bot khác với rule được design ( đảm bảo các dữ liệu y khoa được chính xác 100% )
   - Nếu tìm thấy: đưa vào prompt và gọi LLM
6. **System Prompt cho LLM:**
   ```
   Bạn là trợ lý y tế AI của Bệnh viện [Tim Hà Nội]. Bạn CHỈ được trả lời dựa trên hoặc ưu tiên dựa vào
   thông tin được cung cấp trong phần CONTEXT bên dưới. KHÔNG ĐƯỢC bịa thông tin
   hoặc lấy từ nguồn bên ngoài. Hãy trả lời ngắn gọn, súc tích và đi thẳng vào vấn đề, ưu tiên sử dụng Tiếng Việt.

   Nếu câu hỏi nằm ngoài phạm vi CONTEXT, hãy tuân thủ theo rule và đảm bảo các dữ liệu có nguồn chính thống
    nói: "Xin lỗi, tôi không có
   thông tin về vấn đề này. Vui lòng liên hệ bác sĩ để được tư vấn trực tiếp." và đồng thời hãy gợi ý 
   liên hệ với một số điện thoại hỗ trợ y tế đã được cung cấp.

   CONTEXT:
   {retrieved_chunks}
   ```
7. **API Endpoint:**
   - `POST /api/ai/chat` — Chat với AI (có auth)
   - `GET /api/ai/health` — Health check
   - `POST /api/ai/feedback` — Người dùng phản hồi chất lượng câu trả lời

#### 2.3 Kết Nối Flask ↔ FastAPI
- Flask backend proxy request đến FastAPI AI service qua HTTP internal
- Hoặc frontend gọi trực tiếp FastAPI (cấu hình CORS phù hợp)
- Docker Compose quản lý cả 2 services

---

### 🏥 3. FRONTEND — WEBSITE BỆNH VIỆN

#### 3.1 Các Trang Cần Xây

| Trang | File | Mô tả |
|-------|------|--------|
| **Trang chủ** | `index.html` | Hero banner, giới thiệu bệnh viện, chuyên khoa, CTA đặt lịch |
| **Đăng nhập** | `login.html` | Giữ nguyên hạ tầng Firebase Auth (Google + Email) |
| **Đặt lịch hẹn** | `appointment.html` | ⭐ Form đặt lịch khám (chọn khoa, bác sĩ, ngày giờ) |
| **Danh sách chuyên khoa** | `departments.html` | Grid các khoa (Nội, Ngoại, Nhi, Sản, Da liễu...) |
| **Thông tin bác sĩ** | `doctors.html` | Profile bác sĩ, chuyên môn, lịch làm việc |
| **Lịch sử khám** | `history.html` | Refactor từ history.html cũ — hiện lịch sử lịch hẹn |
| **AI Tư Vấn Sức Khỏe** | `ai-chat.html` | ⭐ Chat với AI (dùng RAG) — tư vấn triệu chứng |
| **Liên hệ** | `contact.html` | ⭐ Bản đồ, SĐT custom, nút Gọi điện, link Zalo Mini |
| **Giới thiệu** | `about.html` | Refactor — giới thiệu bệnh viện |
| **Tin tức y tế** | `news.html` | Bài viết sức khỏe, tin tức bệnh viện |
| **404** | `404.html` | Error page redesign |

#### 3.2 Tính Năng Đặt Lịch Hẹn (CHI TIẾT)

##### Cấu Trúc Dữ Liệu Firebase RTDB — Node `appointments`

```json
{
  "appointments": {
    "{appointment_id}": {
      "uid": "abc123...",
      "patient_name": "Nguyễn Văn A",
      "patient_phone": "0901234567",
      "patient_email": "nguyenvana@gmail.com",
      "patient_dob": "1990-05-15",
      "patient_gender": "male",
      "department_id": "noi_khoa",
      "department_name": "Nội khoa",
      "doctor_id": "bs001",
      "doctor_name": "BS. Trần Văn B",
      "appointment_date": "2026-07-25",
      "appointment_time": "09:00",
      "time_slot": "09:00-09:30",
      "reason": "Đau đầu, chóng mặt kéo dài 3 ngày",
      "symptoms": ["đau đầu", "chóng mặt"],
      "priority": "normal",
      "status": "pending",
      "notes": "",
      "created_at": "2026-07-18T08:30:00Z",
      "updated_at": "2026-07-18T08:30:00Z",
      "confirmed_by": "",
      "cancelled_reason": ""
    }
  }
}
```

**Status flow:** `pending` → `confirmed` → `completed` | `cancelled` | `no_show`

##### Node `departments` (Danh sách khoa)

```json
{
  "departments": {
    "noi_khoa": {
      "name": "Nội khoa",
      "description": "Khám và điều trị các bệnh nội khoa tổng quát",
      "icon": "🫀",
      "image": "...",
      "working_hours": "07:00 - 17:00",
      "phone": "028-1234-5601",
      "is_active": true,
      "order": 1
    }
  }
}
```

##### Node `doctors` (Thông tin bác sĩ)

```json
{
  "doctors": {
    "bs001": {
      "name": "BS. Trần Văn B",
      "title": "ThS.BS",
      "department_id": "noi_khoa",
      "specialty": "Tim mạch, Huyết áp",
      "avatar": "https://...",
      "bio": "15 năm kinh nghiệm...",
      "schedule": {
        "monday": ["08:00-12:00", "14:00-17:00"],
        "tuesday": ["08:00-12:00"],
        "wednesday": ["08:00-12:00", "14:00-17:00"],
        "thursday": [],
        "friday": ["08:00-12:00", "14:00-17:00"],
        "saturday": ["08:00-12:00"],
        "sunday": []
      },
      "is_active": true,
      "order": 1
    }
  }
}
```

##### Node `time_slots` (Quản lý slot thời gian)

```json
{
  "time_slots": {
    "2026-07-25": {
      "bs001": {
        "09:00": { "status": "booked", "appointment_id": "apt001" },
        "09:30": { "status": "available" },
        "10:00": { "status": "available" }
      }
    }
  }
}
```

##### Thao Tác Trên Firebase

| Thao tác | Phía | Chi tiết |
|----------|------|----------|
| **Tạo lịch hẹn** | Frontend (user) | Push vào `appointments/`, set status=`pending` |
| **Kiểm tra slot** | Frontend | Read `time_slots/{date}/{doctor_id}` |
| **Book slot** | Frontend + Backend | Transaction: check available → set booked |
| **Confirm lịch hẹn** | Backend (admin/bác sĩ) | Update status=`confirmed`, gửi notification |
| **Hủy lịch hẹn** | Frontend (user) / Backend | Update status=`cancelled`, free slot |
| **Lịch sử khám** | Frontend | Query `appointments/` by uid |
| **Xem tất cả** | Backend (admin) | Read all `appointments/` |

#### 3.3 Tính Năng Zalo Mini + Gọi Điện

##### Nút Gọi Điện
```html
<!-- Số điện thoại được custom trong Firebase config -->
<a href="tel:{HOSPITAL_PHONE}" class="call-btn">
  📞 Gọi ngay: {HOSPITAL_PHONE}
</a>
```

##### Tích Hợp Zalo
```html
<!-- Link Zalo Mini App / OA Chat -->
<a href="https://zalo.me/{ZALO_OA_ID}" class="zalo-btn" target="_blank">
  💬 Chat qua Zalo
</a>

<!-- Zalo OA Widget (optional) -->
<div class="zalo-chat-widget"
     data-oaid="{ZALO_OA_ID}"
     data-welcome-message="Xin chào! Bệnh viện có thể giúp gì cho bạn?"
     data-autopopup="0"
     data-width="350"
     data-height="420">
</div>
<script src="https://sp.zalo.me/plugins/sdk.js"></script>
```

##### Node `hospital_config` (Firebase — Cấu hình custom)

```json
{
  "hospital_config": {
    "name": "Bệnh Viện Đa Khoa XYZ",
    "phone": "028-1234-5600",
    "hotline": "1900-xxxx",
    "emergency": "115",
    "email": "info@benhvienxyz.vn",
    "address": "123 Nguyễn Văn Cừ, Q.5, TP.HCM",
    "zalo_oa_id": "1234567890",
    "zalo_mini_app_url": "https://zalo.me/s/...",
    "google_maps_embed": "https://www.google.com/maps/embed?...",
    "working_hours": "07:00 - 20:00 (Thứ 2 - Thứ 7)",
    "social_links": {
      "facebook": "https://facebook.com/benhvienxyz",
      "youtube": "https://youtube.com/@benhvienxyz"
    }
  }
}
```

> **Quan trọng:** Tất cả SĐT, link Zalo, thông tin liên hệ phải được **đọc từ Firebase
> `hospital_config`**, không hardcode trong HTML. Admin có thể thay đổi bất cứ lúc nào.

---

### 🔒 4. BẢO MẬT (KHÔNG ĐƯỢC BỎ QUA)

#### 4.1 Firebase Security Rules — Thiết Kế Mới

```json
{
  "rules": {
    ".read": false,
    ".write": false,

    "users": {
      "$uid": {
        ".read": "auth != null && ($uid === auth.uid || root.child('users/' + auth.uid + '/role').val() === 'admin' || root.child('users/' + auth.uid + '/role').val() === 'doctor')",
        ".write": "auth != null && (auth.uid === $uid || root.child('users/' + auth.uid + '/role').val() === 'admin')",
        "role": {
          ".validate": "(!data.exists() && newData.val() === 'patient') || (data.exists() && newData.val() === data.val()) || root.child('users/' + auth.uid + '/role').val() === 'admin'"
        }
      }
    },

    "appointments": {
      ".indexOn": ["uid", "status", "appointment_date", "doctor_id"],
      "$appointment_id": {
        ".read": "auth != null && (data.child('uid').val() === auth.uid || root.child('users/' + auth.uid + '/role').val() === 'admin' || root.child('users/' + auth.uid + '/role').val() === 'doctor')",
        ".write": "auth != null && (!data.exists() ? newData.child('uid').val() === auth.uid && newData.child('status').val() === 'pending' : (data.child('uid').val() === auth.uid && data.child('status').val() === 'pending' && newData.child('status').val() === 'cancelled') || root.child('users/' + auth.uid + '/role').val() === 'admin' || root.child('users/' + auth.uid + '/role').val() === 'doctor')"
      }
    },

    "departments": {
      ".read": true,
      ".write": "auth != null && root.child('users/' + auth.uid + '/role').val() === 'admin'"
    },

    "doctors": {
      ".read": true,
      ".write": "auth != null && root.child('users/' + auth.uid + '/role').val() === 'admin'"
    },

    "time_slots": {
      ".read": true,
      ".write": "auth != null"
    },

    "hospital_config": {
      ".read": true,
      ".write": "auth != null && root.child('users/' + auth.uid + '/role').val() === 'admin'"
    },

    "ai_conversations": {
      "$uid": {
        ".read": "auth != null && $uid === auth.uid",
        ".write": "auth != null && $uid === auth.uid"
      }
    },

    "news": {
      ".read": true,
      ".write": "auth != null && root.child('users/' + auth.uid + '/role').val() === 'admin'"
    }
  }
}
```

#### 4.2 Checklist Bảo Mật Bắt Buộc

- [ ] **Thông tin y tế nhạy cảm:** KHÔNG lưu kết quả xét nghiệm, chẩn đoán chi tiết trên
      Firebase RTDB (chỉ lưu metadata lịch hẹn). Dữ liệu y tế nhạy cảm phải qua backend.
- [ ] **CORS:** Chỉ cho phép domain production + localhost dev
- [ ] **Rate Limiting:** API đặt lịch: max 5 request/phút/user
- [ ] **Input Validation:** Validate SĐT (regex VN), email, ngày tháng ở cả frontend + backend
- [ ] **JWT:** Không lưu thông tin nhạy cảm trong JWT payload
- [ ] **Firebase Rules:** Test với Firebase Emulator Suite trước khi deploy
- [ ] **HTTPS only:** Tất cả API calls phải qua HTTPS
- [ ] **XSS Prevention:** Sanitize user input trước khi render
- [ ] **Admin SDK:** Chỉ backend mới dùng Admin SDK (bypass rules)
- [ ] **Environment Variables:** Tất cả secrets trong .env, KHÔNG hardcode
- [ ] **AI Safety:** AI không được đưa ra chẩn đoán y khoa — chỉ tư vấn tổng quát + khuyên gặp bác sĩ
- [ ] **Logging:** Log tất cả thao tác quan trọng (đặt lịch, hủy lịch, admin actions)
- [ ] **Zalo OA ID:** Đọc từ Firebase config, không hardcode

---

### 🎨 5. THIẾT KẾ GIAO DIỆN

#### 5.1 Nguyên Tắc Design

- **Tone:** Chuyên nghiệp y tế, sạch sẽ, đáng tin cậy (KHÔNG dùng tone cyberpunk/neon cũ)
- **Color Palette:**
  - Primary: `#0077B6` (xanh dương y tế)
  - Secondary: `#00B4D8` (xanh nhạt)
  - Accent: `#90E0EF` (teal nhạt)
  - Background: `#FFFFFF` / `#F8F9FA`
  - Text: `#212529`
  - Success: `#2DC653`
  - Warning: `#FFC107`
  - Danger: `#E63946`
- **Typography:** Google Fonts — `Inter` hoặc `Nunito` (friendly, readable)
- **Responsive:** Mobile-first, hỗ trợ tốt trên điện thoại (bệnh nhân hay dùng mobile)
- **Accessibility:** Contrast ratio ≥ 4.5:1, focus states, alt texts
- **Animations:** Subtle, professional — không quá flashy

#### 5.2 Design System Mới (`css/hospital-design.css`)

Đảm bảo về mặt UI/UX hiển thị một cách tinh tế trực quan không sử dụng các hình ảnh hoặc màu sắc rực rỡ gây chú ý khiến thông tin dễ bị sao nhãng. Hã

---

### 🔄 6. PHÂN QUYỀN (ROLE SYSTEM)

| Role | Mã | Quyền |
|------|----|-------|
| **Bệnh nhân** | `patient` | Đặt lịch, xem lịch sử, chat AI, hủy lịch pending |
| **Bác sĩ** | `doctor` | Xem lịch hẹn của mình, confirm/complete, xem bệnh nhân |
| **Admin** | `admin` | Toàn quyền: CRUD departments, doctors, appointments, config |

> Thay thế role cũ: `student` → `patient`, `teacher` → `admin`, thêm `doctor`.

---

### 📋 7. BACKEND API MỚI

#### 7.1 Flask API Endpoints

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| POST | `/api/auth/register` | ❌ | Đăng ký (role=patient mặc định) |
| POST | `/api/auth/login` | ❌ | Đăng nhập |
| GET | `/api/auth/profile` | 🔒 | Profile |
| PUT | `/api/auth/profile` | 🔒 | Cập nhật profile |
| POST | `/api/auth/sync` | ❌ | Sync OAuth |
| GET | `/api/appointments` | 🔒 | Lịch hẹn của user |
| POST | `/api/appointments` | 🔒 | Tạo lịch hẹn mới |
| PUT | `/api/appointments/<id>/cancel` | 🔒 | Hủy lịch hẹn |
| PUT | `/api/appointments/<id>/confirm` | 🔒🩺 | Bác sĩ confirm |
| PUT | `/api/appointments/<id>/complete` | 🔒🩺 | Bác sĩ hoàn thành |
| GET | `/api/departments` | ❌ | Danh sách khoa |
| GET | `/api/doctors` | ❌ | Danh sách bác sĩ |
| GET | `/api/doctors/<id>/slots` | ❌ | Slot trống của bác sĩ |
| GET | `/api/config` | ❌ | Hospital config (SĐT, Zalo...) |
| GET | `/api/news` | ❌ | Tin tức y tế |
| GET | `/api/health` | ❌ | Health check |
| GET | `/api/stats` | ❌ | Stats (tổng bệnh nhân, lịch hẹn hôm nay...) |

#### 7.2 FastAPI AI Endpoints (Port riêng)

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| POST | `/api/ai/chat` | 🔒 | Chat với AI (RAG) |
| GET | `/api/ai/health` | ❌ | AI service health |
| POST | `/api/ai/feedback` | 🔒 | Phản hồi chất lượng |

---

### 🗑️ 8. NHỮNG GÌ CẦN XÓA

- `backend/core/compiler.py` — Compiler đa ngôn ngữ
- `backend/core/judge.py` — Judge engine
- `backend/models/submission.py` → Refactor thành `appointment.py`, `department.py`
- `backend/routes/playground_routes.py` → Thay bằng `appointment_routes.py`
- Frontend: `problems.html`, `solve.html`, `playground.html`, `contest.html`,
  `contest_room.html`, `essay.html`, `rank.html`
- CSS: `neo-design.css` → Thay bằng `hospital-design.css`
- Firebase nodes: `problems`, `submissions`, `contest_submissions`, `contests`,
  `ai_requests`, `public_leaderboard`

---

### ✅ 9. VERIFICATION CHECKLIST

Sau khi hoàn thành, kiểm tra:

- [ ] Tất cả trang frontend hoạt động trên mobile
- [ ] Đặt lịch hẹn end-to-end: chọn khoa → bác sĩ → ngày → giờ → xác nhận
- [ ] AI chat trả lời DỰA TRÊN DATASET, từ chối câu hỏi ngoài phạm vi
- [ ] Firebase rules đúng: patient chỉ xem lịch mình, doctor xem lịch được assign
- [ ] Nút gọi điện hoạt động trên mobile (tel: protocol)
- [ ] Link Zalo mở đúng OA/Mini App
- [ ] SĐT và Zalo OA ID đọc từ Firebase config, thay đổi được
- [ ] Login/Register hoạt động (Google OAuth + Email)
- [ ] JWT token refresh hoạt động
- [ ] Rate limiting trên API đặt lịch
- [ ] Docker Compose chạy cả Flask + FastAPI + Redis
- [ ] Logging hoạt động đúng
- [ ] Không có hardcoded secrets trong code

---

### 🚀 10. THỨ TỰ THỰC HIỆN ĐỀ XUẤT

1. **Phase 1:** Refactor backend — Xóa judge/compiler, tạo models mới, API endpoints mới
2. **Phase 2:** Firebase — Thiết kế lại data structure, security rules, seed data
3. **Phase 3:** AI Service — Setup FastAPI + RAG pipeline + vector store
4. **Phase 4:** Frontend — Redesign CSS, xây dựng các trang mới
5. **Phase 5:** Tích hợp — Kết nối frontend ↔ backend ↔ AI ↔ Firebase
6. **Phase 6:** Testing — End-to-end testing, security audit, mobile testing
7. **Phase 7:** Deployment — Docker Compose, Firebase Hosting, DNS config
```

---

> ⚠️ **LƯU Ý QUAN TRỌNG:**
> - AI CHỈ ĐƯỢC tư vấn tổng quát. Mọi câu trả lời PHẢI kèm disclaimer:
>   *"Thông tin này chỉ mang tính tham khảo. Vui lòng đến gặp bác sĩ để được tư vấn chính xác."*
> - Không lưu trữ thông tin y tế nhạy cảm (kết quả xét nghiệm, chẩn đoán) trên client-side.
> - Tuân thủ pháp luật Việt Nam.
```
