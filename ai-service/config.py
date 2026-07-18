"""
AI Service Configuration
Đọc biến môi trường từ .env và cung cấp settings cho toàn bộ AI service.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Centralized settings cho AI Service."""

    # NVIDIA NIM API
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-70b-instruct")
    NVIDIA_EMBED_MODEL: str = os.getenv("NVIDIA_EMBED_MODEL", "nvidia/nv-embedqa-e5-v5")
    NVIDIA_BASE_URL: str = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")

    # Server
    HOST: str = os.getenv("AI_SERVICE_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("AI_SERVICE_PORT", "8001"))
    ALLOWED_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:8001,http://127.0.0.1:8001"
        ).split(",")
        if origin.strip()
    ]
    CHAT_RATE_LIMIT_PER_MINUTE: int = int(
        os.getenv("CHAT_RATE_LIMIT_PER_MINUTE", "10")
    )

    # RAG Pipeline
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "400"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    TOP_K: int = int(os.getenv("TOP_K", "4"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.60"))

    # Data
    DATA_DIR: str = os.getenv(
        "DATA_DIR",
        str(Path(__file__).resolve().parent.parent / "Data")
    )
    KNOWLEDGE_APPROVED_DIR: str = os.getenv(
        "KNOWLEDGE_APPROVED_DIR",
        str(Path(__file__).resolve().parent.parent / "knowledge" / "approved")
    )

    # Hospital Info (hardcoded — dữ liệu chính thống)
    HOSPITAL_NAME: str = "Bệnh viện Tim Hà Nội"
    HOSPITAL_HOTLINE: str = "19001082"
    HOSPITAL_CSKH_PHONES: list = ["0837091082", "0836761082"]
    HOSPITAL_EMAIL: str = "cskh@timhanoi.vn"
    HOSPITAL_EMERGENCY: str = "115"
    HOSPITAL_ADDRESS_1: str = "Số 92 Trần Hưng Đạo, phường Cửa Nam, Hà Nội"
    HOSPITAL_ADDRESS_2: str = "Số 695 Lạc Long Quân, phường Tây Hồ, Hà Nội"
    HOSPITAL_BOOKING_URL: str = "https://benhvientimhanoi.vn/he-thong/hen-kham/index.html"
    HOSPITAL_WEBSITE: str = "https://benhvientimhanoi.vn"
    HOSPITAL_PKDK_PHONE: str = "0243.758.9090"
    HOSPITAL_SOCIAL_PHONE: str = "0243.942.5880"

    @classmethod
    def validate(cls) -> list[str]:
        """Kiểm tra các settings bắt buộc."""
        errors = []
        if not cls.NVIDIA_API_KEY:
            errors.append("NVIDIA_API_KEY chưa được cấu hình trong .env")
        if not Path(cls.DATA_DIR).exists():
            errors.append(f"DATA_DIR không tồn tại: {cls.DATA_DIR}")
        return errors


settings = Settings()
