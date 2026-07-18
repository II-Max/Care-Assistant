"""
Chat Service — Full RAG pipeline xử lý chat.

Luồng xử lý:
1. Emergency Detection → nếu cấp cứu → return emergency response
2. Embed query → Retrieve top-K chunks
3. Kiểm tra similarity threshold
4. Build augmented prompt (system + context + query)
5. Call LLM (NVIDIA NIM)
6. Append disclaimer + source citations
7. Log to Firebase (conversation, messages, audit)
"""

import time
import json
import logging
from typing import Optional
from datetime import datetime

from openai import AsyncOpenAI

from config import settings
from rag.retriever import retriever
from services.emergency_detector import emergency_detector
from models.schemas import ChatResponse, Source

# Firebase (optional — fallback nếu không có)
try:
    from services.firebase import firebase_client, hash_ip
    from services.firebase.schemas import Conversation, Message, AuditLog, EmergencyLog
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    firebase_client = None
    hash_ip = lambda x: x[:16]
    Conversation = Message = AuditLog = EmergencyLog = None

logger = logging.getLogger("chat_service")


# System Prompt — Tuân thủ Trustworthy AI guidelines
SYSTEM_PROMPT = """Bạn là Trợ lý Chăm sóc Khách hàng AI của Bệnh viện Tim Hà Nội — bệnh viện chuyên khoa tim mạch hạng I, tuyến cuối của cả nước.

QUY TẮC BẮT BUỘC (PHẢI TUÂN THỦ TUYỆT ĐỐI):

1. **CHỈ trả lời dựa trên thông tin trong phần [CONTEXT] được cung cấp bên dưới.** Không được tự bịa, suy đoán, hay lấy thông tin từ nguồn ngoài.

2. **KHÔNG BAO GIỜ** đưa ra:
   - Chẩn đoán bệnh
   - Tư vấn điều trị hoặc dùng thuốc
   - Kết luận y khoa
   - Dự đoán tiên lượng bệnh

3. Nếu CONTEXT không chứa thông tin liên quan đến câu hỏi, trả lời:
   "Xin lỗi, tôi chưa có thông tin về vấn đề này. Quý khách vui lòng liên hệ Tổng đài 19001082 (Thứ 2 – Thứ 7, 8h – 16h) để được hỗ trợ trực tiếp."

4. Nếu câu hỏi liên quan đến triệu chứng bệnh hoặc tình trạng sức khỏe → khuyên gặp bác sĩ, KHÔNG tư vấn y tế.

5. Luôn trả lời bằng tiếng Việt, lịch sự, chuyên nghiệp, ngắn gọn và đi thẳng vào vấn đề.

6. **Tự động sửa lỗi NLP:** Dùng khả năng suy luận ngữ cảnh để hiểu ý người dùng nếu họ viết sai chính tả.

7. **BẮT BUỘC TRẢ VỀ JSON:** Mọi phản hồi của bạn phải theo định dạng JSON sau, không được kèm bất kỳ chữ nào bên ngoài JSON:
{{
    "risk_level": "LOW",  // LOW (câu hỏi thường), MEDIUM (hỏi triệu chứng), HIGH (cấp cứu)
    "handoff_required": false, // True nếu vượt quá khả năng hoặc cần bác sĩ tư vấn
    "answer": "Câu trả lời của bạn, chứa thông tin liên hệ và disclaimer ở cuối."
}}

8. Khi cung cấp thông tin liên hệ:
   - Hotline đặt khám: 19001082 | CSKH: 0837091082 / 0836761082
   - Đặt khám online: https://benhvientimhanoi.vn/he-thong/hen-kham/index.html

9. Cuối mỗi `answer`, LUÔN thêm disclaimer:
   "📋 *Thông tin này chỉ mang tính tham khảo. Vui lòng liên hệ bệnh viện để được tư vấn chính xác.*"

CONTEXT:
{context}"""

# Khi không có context
NO_CONTEXT_RESPONSE = """Xin lỗi, tôi chưa có thông tin về vấn đề này trong cơ sở dữ liệu.

Quý khách vui lòng liên hệ để được hỗ trợ trực tiếp:
📞 **Tổng đài:** 19001082 (Thứ 2 – Thứ 7, 8h – 16h)
📞 **CSKH:** 0837091082 | 0836761082
📧 **Email:** cskh@timhanoi.vn
🌐 **Website:** [benhvientimhanoi.vn](https://benhvientimhanoi.vn)

📋 *Thông tin này chỉ mang tính tham khảo. Vui lòng liên hệ bệnh viện để được tư vấn chính xác.*"""


class ChatService:
    """Xử lý chat RAG pipeline + logging Firebase."""

    def __init__(self):
        self.client: Optional[AsyncOpenAI] = None
        self._conversation_counter = 0  # Tạo conversation ID tạm

    def initialize(self):
        """Khởi tạo LLM client + Firebase."""
        # Init LLM
        try:
            self.client = AsyncOpenAI(
                api_key=settings.NVIDIA_API_KEY,
                base_url=settings.NVIDIA_BASE_URL
            )
            logger.info("✅ Chat Service initialized")
        except Exception as e:
            logger.error(f"❌ LLM init failed: {e}")
            raise

        # Init Firebase (optional)
        if FIREBASE_AVAILABLE and firebase_client:
            firebase_client.initialize()
            if firebase_client.is_ready:
                logger.info("✅ Firebase integrated with Chat Service")
            else:
                logger.info("ℹ️ Firebase in fallback mode (offline logging)")
        else:
            logger.info("ℹ️ Firebase not available (offline mode)")

    def _generate_conversation_id(self, user_ip: str) -> str:
        """Tạo conversation ID dựa trên IP + timestamp."""
        self._conversation_counter += 1
        ts = int(time.time() * 1000)
        ip_hash = hash_ip(user_ip) if user_ip else "anon"
        return f"conv_{ts}_{self._conversation_counter}_{ip_hash[:8]}"

    async def chat(self, message: str, 
                   conversation_id: Optional[str] = None,
                   user_ip: str = "",
                   user_agent: str = "") -> ChatResponse:
        """Xử lý một tin nhắn chat.

        Pipeline:
        1. Emergency check
        2. RAG retrieve
        3. LLM generate
        4. Format response
        """
        # ============================
        # Khởi tạo metrics
        # ============================
        start_ns = time.monotonic_ns()
        is_emergency_result = False
        is_error = False
        error_type = None
        error_msg = None

        # Tạo/gán conversation ID
        conv_id = conversation_id or self._generate_conversation_id(user_ip)

        # ============================
        # Step 1: Emergency Detection
        # ============================
        emergency_result = emergency_detector.detect(message)

        if emergency_result["is_emergency"]:
            elapsed_ms = (time.monotonic_ns() - start_ns) // 1_000_000

            # Log emergency to Firebase
            if FIREBASE_AVAILABLE and firebase_client and firebase_client.is_ready:
                firebase_client.add_emergency_log(EmergencyLog(
                    user_message=message,
                    matched_keywords=emergency_result.get("matched_keywords", []),
                    response_sent=emergency_result["response"],
                    response_time_ms=elapsed_ms,
                    conversation_id=conv_id,
                    user_ip_hash=hash_ip(user_ip)
                ).to_dict())

            return ChatResponse(
                reply=emergency_result["response"],
                sources=[],
                is_emergency=True,
                confidence=1.0,
                risk_level="HIGH",
                handoff_required=True
            )

        # ============================
        # Step 2: RAG Retrieval
        # ============================
        results = retriever.retrieve(message)

        # ============================
        # Step 3: Build Context & Call LLM
        # ============================
        if not results:
            context = "KHÔNG CÓ THÔNG TIN. Hãy khuyên bệnh nhân liên hệ tổng đài."
            sources = []
            max_score = 0.0
            retrieval_count = 0
        else:
            context = retriever.build_context(results)
            sources = retriever.get_sources(results)
            max_score = max(r.score for r in results)
            retrieval_count = len(results)

        # Build system prompt với context
        system_message = SYSTEM_PROMPT.format(context=context)

        try:
            response = await self.client.chat.completions.create(
                model=settings.NVIDIA_MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": message}
                ],
                max_tokens=1024,
                temperature=0.1,  # Rất thấp để format JSON chính xác
                top_p=0.9,
                response_format={"type": "json_object"}
            )

            raw_reply = response.choices[0].message.content.strip()
            
            try:
                parsed = json.loads(raw_reply)
                reply = parsed.get("answer", "")
                risk_level = parsed.get("risk_level", "LOW")
                handoff_required = parsed.get("handoff_required", False)
            except json.JSONDecodeError:
                reply = raw_reply
                risk_level = "LOW"
                handoff_required = False

        except Exception as e:
            logger.error(f"❌ LLM call failed: {e}")
            is_error = True
            error_type = "llm_call_failed"
            error_msg = str(e)[:200]
            reply = (
                "Xin lỗi, hiện tại hệ thống đang gặp sự cố kỹ thuật. "
                "Quý khách vui lòng thử lại sau hoặc liên hệ Tổng đài **19001082** để được hỗ trợ."
            )
            elapsed_ms = (time.monotonic_ns() - start_ns) // 1_000_000

            # Log audit error
            if FIREBASE_AVAILABLE and firebase_client and firebase_client.is_ready:
                firebase_client.add_audit_log(AuditLog(
                    event_type="error",
                    conversation_id=conv_id,
                    risk_level="LOW",
                    confidence=0.0,
                    latency_ms=elapsed_ms,
                    retrieval_count=0,
                    error_type=error_type,
                    error_message=error_msg,
                    user_ip_hash=hash_ip(user_ip)
                ).to_dict())

            return ChatResponse(
                reply=reply,
                sources=[],
                is_emergency=False,
                confidence=0.0,
                risk_level="LOW",
                handoff_required=False
            )

        # ============================
        # Step 4: Post-processing
        # ============================
        elapsed_ms = (time.monotonic_ns() - start_ns) // 1_000_000

        # Nếu URGENT → prepend khuyến nghị
        if emergency_result["is_urgent"]:
            reply = emergency_result["response"] + "\n\n" + reply
            risk_level = "HIGH"
            handoff_required = True
            is_emergency_result = True

        # Đảm bảo disclaimer có trong response
        if "tham khảo" not in reply.lower() and "liên hệ bệnh viện" not in reply.lower():
            reply += "\n\n📋 *Thông tin này chỉ mang tính tham khảo. Vui lòng liên hệ bệnh viện để được tư vấn chính xác.*"

        # ============================
        # Step 5: Log to Firebase (async-safe)
        # ============================
        if FIREBASE_AVAILABLE and firebase_client and firebase_client.is_ready:
            try:
                # Tạo conversation mới nếu chưa có
                existing = firebase_client.get_conversation(conv_id)
                if not existing:
                    firebase_client.create_conversation(Conversation(
                        conversation_id=conv_id,
                        user_ip=hash_ip(user_ip),
                        device_info=hash_ip(user_agent) if user_agent else "",
                        start_time=datetime.utcnow(),
                        risk_level=risk_level,
                        emergency_triggered=is_emergency_result
                    ).to_dict())

                # Lưu message
                firebase_client.add_message(conv_id, Message(
                    conversation_id=conv_id,
                    role="user",
                    content=message,
                    risk_level=risk_level,
                    latency_ms=elapsed_ms
                ).to_dict())

                firebase_client.add_message(conv_id, Message(
                    conversation_id=conv_id,
                    role="assistant",
                    content=reply,
                    sources=[{"title": s["title"], "url": s["url"]} for s in sources],
                    risk_level=risk_level,
                    confidence=max_score,
                    handoff_required=handoff_required,
                    is_emergency=is_emergency_result,
                    latency_ms=elapsed_ms,
                    chunks_used=retrieval_count
                ).to_dict())

                # Cập nhật conversation (dùng timestamp thay vì Increment)
                firebase_client.update_conversation(conv_id, {
                    "risk_level": risk_level,
                    "emergency_triggered": is_emergency_result,
                    "handoff_requested": handoff_required,
                    "avg_confidence": max_score,
                    "last_message_at": datetime.utcnow().isoformat()
                })

                # Audit log
                firebase_client.add_audit_log(AuditLog(
                    event_type="chat_sent" if not is_emergency_result else "emergency_detected",
                    conversation_id=conv_id,
                    risk_level=risk_level,
                    confidence=max_score,
                    latency_ms=elapsed_ms,
                    retrieval_count=retrieval_count,
                    emergency_triggered=is_emergency_result,
                    user_ip_hash=hash_ip(user_ip)
                ).to_dict())

            except Exception as fb_err:
                logger.warning(f"⚠️ Firebase log failed (non-critical): {fb_err}")
                # Không crash service — log là non-critical

        # Convert source dicts to Source objects
        source_objects = []
        for src in sources:
            source_objects.append(Source(title=src["title"], url=src["url"]))

        return ChatResponse(
            reply=reply,
            sources=source_objects,
            is_emergency=is_emergency_result,
            confidence=max_score,
            risk_level=risk_level,
            handoff_required=handoff_required
        )


# Singleton instance
chat_service = ChatService()
