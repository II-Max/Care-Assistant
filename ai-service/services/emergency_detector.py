"""Emergency Detector — fail-safe triage for high-risk phrases.

Phase 1 intentionally does not let an LLM downgrade a rule hit. The phrase
list must be reviewed and maintained by clinical staff before deployment.
"""

import re


# ========================
# LAYER 1: KEYWORD RULES
# ========================

EMERGENCY_KEYWORDS = [
    # Triệu chứng cấp cứu tim mạch
    "đau ngực dữ dội", "đau ngực", "tức ngực", "đau tim", "nhồi máu",
    "khó thở", "không thở được", "hết hơi", "nghẹt thở", "thở không nổi",
    "ngất xỉu", "ngất", "bất tỉnh", "hôn mê", "mất ý thức",
    "tim đập nhanh", "tim đập bất thường", "rối loạn nhịp tim", "tim ngừng đập",
    "co giật", "tím tái", "tím môi", "tím da",
    "ngừng thở", "ngừng tim",
    "đột quỵ", "liệt nửa người", "méo miệng", "nói ngọng đột ngột",
    "chảy máu không cầm", "xuất huyết",
    "sốc", "trụy tim", "trụy mạch",
    "đau đầu dữ dội", "đau đầu đột ngột", "đau đầu", "nhức đầu", "chóng mặt",
    "đau bụng", "buồn nôn",

    # Tình huống khẩn cấp
    "cấp cứu", "nguy kịch", "sắp chết", "hấp hối",
    "tai nạn", "bị thương nặng",

    # Tiếng Anh phổ biến
    "chest pain", "heart attack", "cardiac arrest",
    "shortness of breath", "fainting", "unconscious",
    "stroke", "emergency", "seizure",
]

# Pattern compiled cho matching nhanh
EMERGENCY_PATTERN = re.compile(
    r"|".join(re.escape(kw) for kw in EMERGENCY_KEYWORDS),
    re.IGNORECASE
)


# ========================
# EMERGENCY RESPONSE
# ========================

EMERGENCY_RESPONSE = """🚨 **CẢNH BÁO CẤP CỨU — HÀNH ĐỘNG NGAY LẬP TỨC**

Dựa trên mô tả của bạn, đây có thể là **tình huống y tế khẩn cấp**. Vui lòng thực hiện NGAY:

**1. Gọi Cấp cứu: 📞 115**
**2. Đến Khoa Cấp cứu Bệnh viện Tim Hà Nội:**
   - 🏥 Cơ sở 1: Số 92 Trần Hưng Đạo, Cửa Nam, Hà Nội
   - 🏥 Cơ sở 2: Số 695 Lạc Long Quân, Tây Hồ, Hà Nội
**3. Hotline Bệnh viện: 📞 19001082**

⚠️ **Lưu ý quan trọng:**
- Không tiếp tục chat để chờ tư vấn.
- Không tự ý dùng thuốc hoặc điều trị tại nhà.

**🚑 HƯỚNG DẪN SƠ CỨU TẠI CHỖ (Trong lúc chờ xe cấp cứu):**
- Đặt người bệnh nằm nghỉ ở tư thế thoải mái (nửa nằm nửa ngồi), nới lỏng quần áo.
- Giữ không gian xung quanh thoáng khí, yên tĩnh.
- Nếu người bệnh bất tỉnh và ngừng thở: Lập tức ép tim ngoài lồng ngực (nhấn mạnh, nhanh ở giữa ngực) liên tục cho đến khi cấp cứu đến.
- TUYỆT ĐỐI KHÔNG tự ý cho người bệnh ăn, uống hay dùng thuốc (trừ thuốc tim mạch đã được bác sĩ kê đơn để dùng khi cấp cứu).

*Tôi là trợ lý AI và KHÔNG có khả năng cung cấp lời khuyên y tế. Hãy liên hệ bác sĩ hoặc dịch vụ cấp cứu ngay lập tức.*"""


URGENT_ADDENDUM = """

⚡ **Khuyến nghị:** Triệu chứng bạn mô tả cần được bác sĩ chuyên khoa tim mạch kiểm tra sớm.
- 📞 Đặt lịch khám: **19001082** (Thứ 2 – Thứ 7, 8h – 16h)
- 🌐 Đặt khám online: [benhvientimhanoi.vn](https://benhvientimhanoi.vn/he-thong/hen-kham/index.html)
- Nếu triệu chứng nặng hơn, hãy đến Khoa Cấp cứu ngay."""


class EmergencyDetector:
    """Phát hiện tình huống cấp cứu y tế."""

    def __init__(self):
        self.is_initialized = False

    def initialize(self):
        """Initialize the deterministic detector."""
        self.is_initialized = True
        print("✅ Emergency Detector initialized (fail-safe rules)")

    def detect(self, message: str) -> dict:
        """Phát hiện cấp cứu trong tin nhắn.

        Returns:
            {
                "level": "EMERGENCY" | "URGENT" | "NORMAL",
                "is_emergency": bool,
                "is_urgent": bool,
                "response": str | None,
                "matched_keywords": list[str]
            }
        """
        result = {
            "level": "NORMAL",
            "is_emergency": False,
            "is_urgent": False,
            "response": None,
            "matched_keywords": []
        }

        # Layer 1: Keyword matching
        keywords_found = EMERGENCY_PATTERN.findall(message.lower())
        result["matched_keywords"] = list(set(keywords_found))

        if keywords_found:
            # Giai đoạn 1 (Update Phase 1): Fail-safe!
            result["level"] = "EMERGENCY"
            result["is_emergency"] = True
            result["response"] = EMERGENCY_RESPONSE

        return result


# Singleton instance
emergency_detector = EmergencyDetector()
