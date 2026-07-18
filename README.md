# 🏥 AI Customer Care Assistant — Bệnh viện Tim Hà Nội
Dự án Hackathon 24h: Phát triển Trợ lý AI y tế thông minh, tích hợp trực tiếp vào hệ thống web của Bệnh viện Tim Hà Nội, hỗ trợ giải đáp tự động các thông tin về dịch vụ, đặt lịch khám và phát hiện tình huống cấp cứu.

---

## 🌟 Tính năng MVP
1. **RAG-based AI Chatbot**: Giải đáp tự động thông tin từ Knowledge Base (thông tin khoa, hướng dẫn đặt khám, bảo hiểm y tế).
2. **Emergency Detection**: Nhận diện triệu chứng khẩn cấp y tế tim mạch (đau ngực dữ dội, khó thở, ngất xỉu) và phản hồi khẩn cấp ngay lập tức với Hotline 115 và địa chỉ bệnh viện.
3. **Trustworthy Guardrails**: AI được chỉ thị tuyệt đối KHÔNG đưa ra lời khuyên y tế hay chẩn đoán bệnh.
4. **Professional UI**: Giao diện website phong cách y tế, sạch sẽ, tin cậy.

---

## 🛠 Kiến trúc hệ thống
Hệ thống gồm 3 thành phần chính:
- `frontend/`: Giao diện web tĩnh (HTML/CSS/JS) với Floating Chat Widget hiện đại.
- `backend/`: Flask server chạy trên `port 5000` (đóng vai trò static server và proxy request).
- `ai-service/`: FastAPI server chạy trên `port 8001` xử lý RAG pipeline, Embedding (FAISS) và gọi LLM (NVIDIA NIM).

---

## 🚀 Hướng dẫn cài đặt & Chạy

### 1. Yêu cầu
- Python 3.9+
- NVIDIA NIM API Key (để sử dụng model `meta/llama-3.1-70b-instruct`)

### 2. Cấu hình
Copy file biến môi trường và điền API key:
```bash
cp .env.example .env
```
Mở file `.env` và thêm:
```
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxx
```

### 3. Khởi động nhanh (Windows)
Chạy script PowerShell sau để tự động cài dependencies và khởi động cả 2 server:
```powershell
.\start.ps1
```

### 4. Truy cập
- **Website Bệnh viện:** `http://localhost:5000`
- **AI Chatbot Full Page:** `http://localhost:5000/ai-chat.html`
- **FastAPI Docs:** `http://localhost:8001/docs`

---
*Dự án phát triển cho mục đích Hackathon.*
