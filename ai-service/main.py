"""
🏥 AI Service — FastAPI Entry Point

Bệnh viện Tim Hà Nội — AI Customer Care Assistant
RAG-based chatbot service với NVIDIA NIM API.

Startup sequence:
1. Load documents từ Data/
2. Chunk documents
3. Tạo embeddings & build FAISS index
4. Initialize Emergency Detector
5. Initialize Chat Service
6. Start FastAPI server

Endpoints:
- POST /api/ai/chat — Chat với AI
- GET  /api/ai/health — Health check
"""

import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette.staticfiles import StaticFiles

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Thêm project root vào sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import settings
from models.schemas import ChatRequest, ChatResponse, HealthResponse
from rag.document_loader import DocumentLoader
from rag.chunker import DocumentChunker
from rag.embedder import embedder
from rag.vector_store import vector_store
from services.emergency_detector import emergency_detector
from services.chat_service import chat_service
from services.rate_limiter import SlidingWindowRateLimiter

# ========================
# App State
# ========================
app_state = {
    "documents_loaded": 0,
    "chunks_indexed": 0,
    "startup_time": 0,
    "is_ready": False
}


# ========================
# Startup / Shutdown
# ========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup & shutdown."""
    print("\n" + "=" * 60)
    print("🏥 AI Service — Bệnh viện Tim Hà Nội")
    print("=" * 60)

    start_time = time.time()

    # Validate settings
    errors = settings.validate()
    if errors:
        for err in errors:
            print(f"❌ {err}")
        print("\n⚠️  Vui lòng cấu hình .env trước khi chạy!")
        print("   Xem .env.example để biết các biến cần thiết.\n")
        # Vẫn start server nhưng đánh dấu chưa ready
    else:
        try:
            # Step 1: Load documents
            print("\n📁 Step 1: Loading documents...")
            loader = DocumentLoader()
            documents = loader.load_all()
            app_state["documents_loaded"] = len(documents)

            # Step 2: Chunk documents
            print("\n✂️  Step 2: Chunking documents...")
            chunker = DocumentChunker()
            chunks = chunker.chunk_documents(documents)

            # Step 3: Initialize embedder & build index
            print("\n🧮 Step 3: Building vector index...")
            embedder.initialize()
            vector_store.build_index(chunks)
            app_state["chunks_indexed"] = vector_store.total_chunks

            # Step 4: Initialize services
            print("\n🔧 Step 4: Initializing services...")
            emergency_detector.initialize()
            chat_service.initialize()

            app_state["is_ready"] = True
            app_state["startup_time"] = time.time() - start_time

            print(f"\n{'=' * 60}")
            print(f"✅ AI Service READY!")
            print(f"   Documents: {app_state['documents_loaded']}")
            print(f"   Chunks:    {app_state['chunks_indexed']}")
            print(f"   Model:     {settings.NVIDIA_MODEL}")
            print(f"   Startup:   {app_state['startup_time']:.1f}s")
            print(f"   URL:       http://localhost:{settings.PORT}")
            print(f"{'=' * 60}\n")

        except Exception as e:
            print(f"\n❌ Startup failed: {e}")
            import traceback
            traceback.print_exc()

    yield

    # Shutdown
    print("\n🛑 AI Service shutting down...")


# ========================
# FastAPI App
# ========================
app = FastAPI(
    title="AI Customer Care — Bệnh viện Tim Hà Nội",
    description="RAG-based AI chatbot cho Bệnh viện Tim Hà Nội",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type", "X-Request-ID"],
)

rate_limiter = SlidingWindowRateLimiter(settings.CHAT_RATE_LIMIT_PER_MINUTE)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"] = "no-store" if request.url.path.startswith("/api/") else "public, max-age=300"
    return response


# ========================
# Endpoints
# ========================

@app.post("/api/ai/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, http_request: Request):
    """Chat với AI — endpoint chính.

    Nhận tin nhắn từ người dùng, xử lý qua RAG pipeline,
    trả về câu trả lời grounded từ Knowledge Base.
    """
    if not app_state["is_ready"]:
        raise HTTPException(
            status_code=503,
            detail="AI Service chưa sẵn sàng. Vui lòng thử lại sau."
        )

    client_ip = http_request.client.host if http_request.client else "unknown"
    if not rate_limiter.allow(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Bạn đã gửi quá nhiều yêu cầu. Vui lòng thử lại sau 1 phút."},
            headers={"Retry-After": "60"}
        )

    try:
        response = await chat_service.chat(
            message=request.message,
            conversation_id=request.conversation_id
        )
        return response
    except Exception as e:
        print(f"❌ Chat error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Lỗi xử lý tin nhắn. Vui lòng thử lại."
        )


@app.get("/api/ai/health", response_model=HealthResponse)
async def health_endpoint():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if app_state["is_ready"] else "starting",
        documents_loaded=app_state["documents_loaded"],
        chunks_indexed=app_state["chunks_indexed"],
        model=settings.NVIDIA_MODEL,
        embedding_model=settings.NVIDIA_EMBED_MODEL
    )


@app.get("/")
async def root():
    """Serve the hospital website from the unified FastAPI application."""
    return FileResponse(FRONTEND_DIR / "index.html")

# Mount static assets after API routes, so API paths always take precedence.
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


# ========================
# Main
# ========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        log_level="info"
    )
