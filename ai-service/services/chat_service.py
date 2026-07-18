"""
Chat Service — Full RAG pipeline xử lý chat.

Luồng xử lý:
1. Emergency Detection → nếu cấp cứu → return emergency response
2. Embed query → Retrieve top-K chunks
3. Kiểm tra similarity threshold
4. Build augmented prompt (system + context + query)
5. Call LLM (NVIDIA NIM)
6. Append disclaimer + source citations
"""

from typing import Optional
from openai import AsyncOpenAI

from config import settings
from rag.retriever import retriever
from services.emergency_detector import emergency_detector
from models.schemas import ChatResponse, Source


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
    """Xử lý chat RAG pipeline."""

    def __init__(self):
        self.client: Optional[AsyncOpenAI] = None

    def initialize(self):
        """Khởi tạo LLM client."""
        try:
            self.client = AsyncOpenAI(
                api_key=settings.NVIDIA_API_KEY,
                base_url=settings.NVIDIA_BASE_URL
            )
            print("✅ Chat Service initialized")
        except Exception as e:
            print(f"❌ Chat Service init failed: {e}")
            raise

    async def chat(self, message: str, conversation_id: Optional[str] = None) -> ChatResponse:
        """Xử lý một tin nhắn chat.

        Pipeline:
        1. Emergency check
        2. RAG retrieve
        3. LLM generate
        4. Format response
        """
        # ============================
        # Step 1: Emergency Detection
        # ============================
        emergency_result = emergency_detector.detect(message)

        if emergency_result["is_emergency"]:
            return ChatResponse(
                reply=emergency_result["response"],
                sources=[],
                is_emergency=True,
                confidence=1.0
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
        else:
            context = retriever.build_context(results)
            sources = retriever.get_sources(results)
            max_score = max(r.score for r in results)

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
            
            import json
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
            print(f"❌ LLM call failed: {e}")
            reply = (
                "Xin lỗi, hiện tại hệ thống đang gặp sự cố kỹ thuật. "
                "Quý khách vui lòng thử lại sau hoặc liên hệ Tổng đài **19001082** để được hỗ trợ."
            )
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

        # Nếu URGENT → prepend khuyến nghị
        if emergency_result["is_urgent"]:
            reply = emergency_result["response"] + "\n\n" + reply
            risk_level = "HIGH"
            handoff_required = True

        # Đảm bảo disclaimer có trong response
        if "tham khảo" not in reply.lower() and "liên hệ bệnh viện" not in reply.lower():
            reply += "\n\n📋 *Thông tin này chỉ mang tính tham khảo. Vui lòng liên hệ bệnh viện để được tư vấn chính xác.*"

        return ChatResponse(
            reply=reply,
            sources=[Source(title=s["title"], url=s["url"]) for s in sources],
            is_emergency=False,
            confidence=max_score,
            risk_level=risk_level,
            handoff_required=handoff_required
        )


# Singleton instance
chat_service = ChatService()
