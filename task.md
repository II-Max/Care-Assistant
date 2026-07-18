# 🏥 Task Tracker — AI Customer Care Assistant

## Phase 1: AI Service (RAG + Emergency Detection) — 0h–6h
- [ ] Setup project structure & .env.example
- [ ] ai-service/config.py — Settings
- [ ] ai-service/models/schemas.py — Pydantic models
- [ ] ai-service/rag/document_loader.py — Load MD + JSON
- [ ] ai-service/rag/chunker.py — Semantic chunking
- [ ] ai-service/rag/embedder.py — Embedding (NVIDIA NIM)
- [ ] ai-service/rag/vector_store.py — FAISS index
- [ ] ai-service/rag/retriever.py — Similarity search
- [ ] ai-service/services/emergency_detector.py — Dual-layer detection
- [ ] ai-service/services/chat_service.py — Full RAG pipeline
- [ ] ai-service/main.py — FastAPI entry point
- [ ] ai-service/requirements.txt
- [ ] Test: RAG pipeline end-to-end

## Phase 2: Frontend — Design System + Chat UI — 6h–12h
- [ ] frontend/css/hospital-design.css — Design system
- [ ] frontend/js/app.js — Shared utilities
- [ ] frontend/js/chat.js — Chat widget logic
- [ ] frontend/index.html — Trang chủ
- [ ] frontend/ai-chat.html — Chat AI full page

## Phase 3: Frontend Pages + Flask Backend — 12h–16h
- [ ] frontend/departments.html
- [ ] frontend/contact.html
- [ ] frontend/about.html
- [ ] backend/app.py — Flask proxy + static serving
- [ ] backend/config.py
- [ ] backend/requirements.txt

## Phase 4: Integration & Polish — 16h–20h
- [ ] Integration test end-to-end
- [ ] Mobile responsive testing
- [ ] Emergency detection validation
- [ ] UI polish & animations

## Phase 5: Ship — 20h–24h
- [ ] Bug fixes
- [ ] README.md update
- [ ] start.ps1 script
- [ ] Defense strategy document
