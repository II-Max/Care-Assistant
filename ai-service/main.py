"""
🏥 AI Service — FastAPI Entry Point

Bệnh viện Tim Hà Nội — AI Customer Care Assistant
RAG-based chatbot service với NVIDIA NIM API.

Phase 3: Booking, Handoff, Departments, Auth.

Startup sequence:
1. Load documents từ Data/
2. Chunk documents
3. Tạo embeddings & build FAISS/ChromaDB index
4. Initialize Emergency Detector
5. Initialize Chat Service
6. Initialize Database connection
7. Start FastAPI server

Endpoints:
- POST /api/ai/chat              — Chat với AI
- GET  /api/ai/health            — Health check
- POST /api/ai/booking           — Đặt lịch khám
- GET  /api/ai/booking/{id}      — Tra cứu lịch hẹn
- POST /api/ai/booking/{id}/cancel — Hủy lịch hẹn
- GET  /api/ai/booking/lookup    — Tra cứu theo số điện thoại
- POST /api/ai/handoff           — Chuyển tiếp nhân viên
- GET  /api/ai/departments       — Danh sách chuyên khoa
- POST /api/ai/feedback          — Feedback
- GET  /api/ai/conversation/{id} — Lịch sử hội thoại
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
from services.booking_service import booking_service, BookingRequest, DEPARTMENTS
from services.handoff_service import handoff_service, HandoffRequest
from database.connection import database

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

            # Step 3: Initialize embedder & build vector index
            print("\n🧮 Step 3: Building vector index...")
            embedder.initialize()
            vector_store.build_index(chunks)
            app_state["chunks_indexed"] = vector_store.total_chunks

            # Step 3b: Initialize BM25 sparse index
            print("\n🔤 Step 3b: Building BM25 sparse index...")
            from rag.bm25_search import bm25_search
            texts = [chunk.embedding_text for chunk in chunks]
            metadatas = [{
                "title": chunk.title,
                "source_url": chunk.source_url,
                "source_file": chunk.source_file,
                "chunk_index": chunk.chunk_index,
                "section_header": chunk.section_header,
            } for chunk in chunks]
            bm25_search.build_index(texts, metadatas)

            # Step 3c: Enable hybrid retrieval
            from rag.retriever import retriever as retriever_singleton
            retriever_singleton.enable_hybrid()

            # Step 4: Initialize database
            print("\n🗄️  Step 4: Initializing database...")
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(database.initialize())
                if database.is_ready:
                    print(f"   ✅ Database ready (PostgreSQL: {database.is_postgres})")
                else:
                    print("   ⚠️  Database not ready")
            except Exception as db_err:
                print(f"   ⚠️  Database init: {db_err}")

            # Step 4b: Initialize Firebase (for logging, booking fallback)
            print("\n☁️  Step 4b: Initializing Firebase...")
            try:
                from services.firebase import firebase_client
                firebase_client.initialize()
                if firebase_client.is_ready:
                    print("   ✅ Firebase ready")
                else:
                    print("   ⚠️  Firebase not configured (offline mode)")
            except Exception as fb_err:
                print(f"   ⚠️  Firebase init: {fb_err}")

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
    Tự động log conversation, messages, audit vào Firebase.
    """
    if not app_state["is_ready"]:
        raise HTTPException(
            status_code=503,
            detail="AI Service chưa sẵn sàng. Vui lòng thử lại sau."
        )

    client_ip = http_request.client.host if http_request.client else "unknown"
    user_agent = http_request.headers.get("User-Agent", "")

    # Rate limiting
    if not rate_limiter.allow(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Bạn đã gửi quá nhiều yêu cầu. Vui lòng thử lại sau 1 phút."},
            headers={"Retry-After": "60"}
        )

    try:
        response = await chat_service.chat(
            message=request.message,
            conversation_id=request.conversation_id,
            user_ip=client_ip,
            user_agent=user_agent
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


@app.post("/api/ai/feedback")
async def feedback_endpoint(request: Request):
    """Nhận feedback từ người dùng về câu trả lời AI.

    Request body:
    {
        "conversation_id": "conv_...",
        "message_id": "msg_...",
        "rating": 4,          # 1-5
        "comment": "Tốt",    # optional
        "category": "general" # general, accuracy, relevance, safety, other
    }
    """
    try:
        data = await request.json()
        conversation_id = data.get("conversation_id", "")
        rating = data.get("rating", 3)
        comment = data.get("comment", "")
        category = data.get("category", "general")
        user_ip = request.client.host if request.client else ""

        # Validate rating
        if not (1 <= rating <= 5):
            return JSONResponse(
                status_code=400,
                content={"detail": "Rating phải từ 1 đến 5."}
            )

        # Log to Firebase nếu có
        from services.firebase import firebase_client, hash_ip
        if firebase_client and firebase_client.is_ready:
            from services.firebase.schemas import Feedback
            firebase_client.add_feedback(Feedback(
                conversation_id=conversation_id or "unknown",
                message_id=data.get("message_id", ""),
                rating=rating,
                comment=comment,
                category=category,
                user_ip=hash_ip(user_ip)
            ).to_dict())

        return {
            "status": "ok",
            "message": "Cảm ơn bạn đã đánh giá! Chúng tôi sẽ cải thiện dịch vụ."
        }

    except Exception as e:
        print(f"❌ Feedback error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Lỗi xử lý feedback."}
        )


@app.get("/api/ai/conversation/{conversation_id}")
async def get_conversation_endpoint(conversation_id: str, request: Request):
    """Lấy lịch sử conversation (cho frontend hiển thị lại)."""
    try:
        from services.firebase import firebase_client
        if firebase_client and firebase_client.is_ready:
            messages = firebase_client.get_conversation_messages(conversation_id)
            conversation = firebase_client.get_conversation(conversation_id)
            return {
                "conversation": conversation or {},
                "messages": messages
            }
        else:
            return {
                "conversation": {},
                "messages": [],
                "note": "Firebase chưa được kết nối. Lịch sử không khả dụng."
            }
    except Exception as e:
        print(f"❌ Get conversation error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Lỗi lấy lịch sử hội thoại."}
        )


# ========================
# Phase 3: Booking Endpoints
# ========================

@app.post("/api/ai/booking")
async def booking_endpoint(http_request: Request):
    """Đặt lịch khám bệnh.

    Request body:
    {
        "patient_name": "Nguyễn Văn A",
        "patient_phone": "0912345678",
        "patient_email": "a@example.com",
        "patient_dob": "1990-01-01",
        "department_id": "noi-khoa",
        "doctor_id": null,
        "booking_date": "2026-07-20",
        "booking_time": "08:00",
        "symptoms": "Đau ngực trái",
        "notes": "",
        "is_bhyt": false,
        "source": "ai_chat"
    }
    """
    try:
        data = await http_request.json()
        client_ip = http_request.client.host if http_request.client else ""

        req = BookingRequest(
            patient_name=data.get("patient_name", ""),
            patient_phone=data.get("patient_phone", ""),
            patient_email=data.get("patient_email", ""),
            patient_dob=data.get("patient_dob"),
            department_id=data.get("department_id", ""),
            doctor_id=data.get("doctor_id"),
            booking_date=data.get("booking_date", ""),
            booking_time=data.get("booking_time", ""),
            symptoms=data.get("symptoms", ""),
            notes=data.get("notes", ""),
            is_bhyt=bool(data.get("is_bhyt", False)),
            source=data.get("source", "ai_chat"),
            user_ip=client_ip
        )

        result = await booking_service.create_booking(req)
        return result

    except Exception as e:
        print(f"❌ Booking error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Hệ thống đang gặp sự cố. Vui lòng gọi Hotline 19001082.",
                "error_code": "SYSTEM_ERROR"
            }
        )


# IMPORTANT: lookup route MUST be registered before {appointment_id} route
# to prevent "lookup" from being matched as an appointment_id.

@app.get("/api/ai/booking/lookup")
async def lookup_bookings_endpoint(http_request: Request):
    """Tra cứu lịch hẹn theo số điện thoại.

    Query params: ?phone=0912345678
    """
    phone = http_request.query_params.get("phone", "")
    if not phone or len(phone) < 10:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "Vui lòng cung cấp số điện thoại."}
        )

    try:
        appointments = await booking_service.get_appointments_by_phone(phone)
        return {
            "success": True,
            "appointments": [
                {
                    "appointment_id": a.get("appointment_id"),
                    "patient_name": a.get("patient_name"),
                    "status": a.get("status"),
                    "booking_date": a.get("booking_date"),
                    "booking_time": a.get("booking_time"),
                    "department_id": a.get("department_id"),
                    "created_at": str(a.get("created_at"))
                }
                for a in appointments
            ]
        }
    except Exception as e:
        print(f"❌ Lookup error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Lỗi tra cứu."}
        )


@app.get("/api/ai/booking/{appointment_id}")
async def get_booking_endpoint(appointment_id: str):
    """Tra cứu thông tin lịch hẹn."""
    try:
        appointment = await booking_service.get_appointment(appointment_id)
        if not appointment:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": "Không tìm thấy lịch hẹn."}
            )
        return {
            "success": True,
            "appointment": {
                "appointment_id": appointment.get("appointment_id"),
                "patient_name": appointment.get("patient_name"),
                "patient_phone": appointment.get("patient_phone", "")[-4:],
                "status": appointment.get("status"),
                "booking_date": appointment.get("booking_date"),
                "booking_time": appointment.get("booking_time"),
                "department_id": appointment.get("department_id"),
                "created_at": appointment.get("created_at")
            }
        }
    except Exception as e:
        print(f"❌ Get booking error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Lỗi tra cứu lịch hẹn."}
        )


@app.post("/api/ai/booking/{appointment_id}/cancel")
async def cancel_booking_endpoint(appointment_id: str, http_request: Request):
    """Hủy lịch hẹn."""
    try:
        data = await http_request.json()
        reason = data.get("reason", "")
        result = await booking_service.cancel_appointment(appointment_id, reason)
        return result
    except Exception as e:
        print(f"❌ Cancel booking error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Lỗi hủy lịch hẹn."}
        )


# ========================
# Phase 3: Handoff Endpoint
# ========================

@app.post("/api/ai/handoff")
async def handoff_endpoint(http_request: Request):
    """Chuyển tiếp yêu cầu cho nhân viên tư vấn.

    Request body:
    {
        "conversation_id": "conv_...",
        "user_message": "Tôi cần tư vấn thêm...",
        "ai_response": "Xin lỗi, tôi chưa có thông tin...",
        "reason": "beyond_capability",
        "patient_phone": "0912345678",
        "patient_name": "Nguyễn Văn A",
        "notes": "",
        "risk_level": "LOW"
    }
    """
    try:
        data = await http_request.json()
        client_ip = http_request.client.host if http_request.client else ""

        req = HandoffRequest(
            conversation_id=data.get("conversation_id", ""),
            user_message=data.get("user_message", ""),
            ai_response=data.get("ai_response", ""),
            reason=data.get("reason", "beyond_capability"),
            patient_phone=data.get("patient_phone", ""),
            patient_name=data.get("patient_name", ""),
            notes=data.get("notes", ""),
            risk_level=data.get("risk_level", "LOW"),
            user_ip=client_ip
        )

        result = await handoff_service.create_handoff(req)
        return result

    except Exception as e:
        print(f"❌ Handoff error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Lỗi tạo yêu cầu hỗ trợ. Vui lòng gọi Hotline 19001082."
            }
        )


# ========================
# Phase 3: Departments Info
# ========================

@app.get("/api/ai/departments")
async def departments_endpoint():
    """Lấy danh sách chuyên khoa."""
    return {
        "success": True,
        "departments": DEPARTMENTS
    }


# ========================
# Frontend Static Files
# ========================

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

@app.get("/")
async def root():
    """Serve the hospital website from the unified FastAPI application."""
    if not FRONTEND_DIR.exists():
        return JSONResponse(content={"status": "API running"})
    return FileResponse(FRONTEND_DIR / "index.html")

# Mount static assets after API routes, so API paths always take precedence.
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
