# 🛡️ Hackathon Defense Strategy — AI Customer Care Assistant

Tài liệu này chuẩn bị chiến lược trình bày (pitching) và trả lời câu hỏi (Q&A) cho dự án AI Customer Care Assistant của Bệnh viện Tim Hà Nội trong vòng chung kết Hackathon.

## 1. The Hook (Mở đầu thu hút - 1 phút)
- **Vấn đề (Pain point):** 3.000 bệnh nhân/ngày. Tổng đài quá tải. Nhân viên y tế kiệt sức vì lặp lại việc trả lời các câu hỏi cơ bản: "Lịch khám mấy giờ?", "Giá siêu âm tim?", "Tôi đau ngực thì làm sao?".
- **Giải pháp (Solution):** Một AI Customer Care Agent trực tiếp trên website.
- **Giá trị (Value):** Giải phóng sức người, phục vụ 24/7, định tuyến khẩn cấp ngay lập tức để cứu người, và hoàn toàn kiểm soát bởi bệnh viện.

## 2. Core Demo (Trình diễn tính năng - 2 phút)
Thể hiện 3 use cases chính trong demo:

### Use Case 1: Tra cứu thông tin mượt mà
- *Input:* "BHYT trái tuyến có được chi trả phẫu thuật tim không?"
- *Output:* AI lấy đúng chính sách BHYT của bệnh viện, kèm nguồn trích dẫn rõ ràng.
- *Điểm nhấn:* RAG Pipeline nội bộ với dữ liệu sạch, chống hallucination tuyệt đối.

### Use Case 2: Guardrails & Trustworthy AI (Bắt buộc với y tế)
- *Input:* "Tôi bị cao huyết áp, nên uống thuốc gì?"
- *Output:* AI từ chối tư vấn y khoa: "Xin lỗi, tôi không thể kê đơn hay tư vấn y khoa. Vui lòng liên hệ bác sĩ..."
- *Điểm nhấn:* AI biết giới hạn của nó, tuân thủ đạo đức y khoa.

### Use Case 3: Emergency Detection (Tính năng "Wow")
- *Input:* "Bố tôi đang bị đau ngực dữ dội, khó thở"
- *Output:* Màn hình giật cảnh báo đỏ 🚨, AI trả về kết quả ngay lập tức yêu cầu gọi 115 và hướng dẫn sơ cứu.
- *Điểm nhấn:* Dual-layer detection (Keyword + LLM) đảm bảo độ trễ siêu thấp và không bỏ sót (100% recall cho cấp cứu).

## 3. Kiến trúc hệ thống (Technical Architecture - 1 phút)
Trình bày kiến trúc đã tối ưu cho 24h Hackathon nhưng dễ dàng scale:
- **LLM:** Sử dụng `meta/llama-3.1-70b-instruct` qua NVIDIA NIM API cho khả năng reasoning và tiếng Việt xuất sắc.
- **Embedding:** NVIDIA NIM `nv-embedqa-e5-v5` / Local fallback, kết hợp FAISS index để semantic search cực nhanh.
- **Backend:** Phân tách rõ ràng: FastAPI cho AI Service (xử lý RAG/Vector) và Flask cho Proxy/Frontend, đảm bảo bảo mật không lộ endpoint AI.
- **RAG Chunker:** Semantic chunker tự viết, tối ưu cho định dạng Markdown y khoa (tách theo heading, merge overlap theo sentence).

## 4. Trả lời Q&A (Dự kiến)

**Q: Tại sao dùng FAISS thay vì VectorDB xịn như Pinecone/Milvus?**
A: Với dataset hiện tại của bệnh viện (FAQ, chính sách, dịch vụ) — số lượng chunks chỉ dưới 5.000. FAISS Flat Index chạy hoàn toàn trên RAM, cho độ trễ search < 10ms, không tốn chi phí hạ tầng hay network IO. Nếu scale lên triệu chunks (hồ sơ bệnh án), kiến trúc cho phép swap sang Milvus dễ dàng qua 1 Interface duy nhất.

**Q: Làm sao đảm bảo AI không tư vấn sai (hallucination) dẫn đến chết người?**
A: Dự án áp dụng 3 lớp bảo vệ (Trustworthy Guardrails):
1. System Prompt quy định rõ tuyệt đối không chẩn đoán.
2. Similarity Threshold cao (0.55): Nếu context không khớp, AI auto-reply "Không có thông tin", không cố bịa.
3. Disclaimer y tế ép cứng (hardcoded) ở mọi câu trả lời.

**Q: Điểm khác biệt so với việc dùng chatbot có sẵn (như ChatGPT custom)?**
A: Data privacy và Emergency Detection. Bệnh viện nắm hoàn toàn DB và luồng xử lý. Dual-layer emergency của chúng em chạy rule-based regex trước (tốn 1ms) để phát hiện từ khóa nguy hiểm, giúp response khẩn cấp ngay lập tức thay vì đợi LLM sinh text (tốn 2-3s). Trong tim mạch, vài giây có thể cứu một mạng người.

## 5. Tương lai (Future Roadmap - Tầm nhìn)
- Tích hợp Voice (Speech-to-Text) cho người già khó gõ phím.
- Kết nối HIS (Hệ thống thông tin bệnh viện) để đặt lịch nội bộ thay vì chỉ cung cấp link.
- Trợ lý cho bác sĩ: Tóm tắt bệnh án từ EHR.