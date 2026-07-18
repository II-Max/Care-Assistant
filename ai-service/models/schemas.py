"""
Pydantic models cho AI Service request/response.
"""

from pydantic import BaseModel, Field
from typing import Optional


class Source(BaseModel):
    """Nguồn thông tin được trích dẫn trong câu trả lời."""
    title: str = Field(description="Tiêu đề tài liệu nguồn")
    url: str = Field(default="", description="URL nguồn (nếu có)")


class ChatRequest(BaseModel):
    """Request gửi tới AI chat endpoint."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Tin nhắn của người dùng"
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="ID phiên hội thoại (để duy trì context)"
    )


class ChatResponse(BaseModel):
    """Response từ AI chat endpoint."""
    reply: str = Field(description="Câu trả lời của AI")
    sources: list[Source] = Field(
        default_factory=list,
        description="Danh sách nguồn thông tin được trích dẫn"
    )
    is_emergency: bool = Field(
        default=False,
        description="Có phải tình huống cấp cứu không"
    )
    confidence: float = Field(
        default=0.0,
        description="Độ tin cậy của câu trả lời (0-1)"
    )
    risk_level: str = Field(
        default="LOW",
        description="Đánh giá rủi ro: LOW, MEDIUM, HIGH"
    )
    handoff_required: bool = Field(
        default=False,
        description="Cần chuyển qua nhân viên tư vấn"
    )


class HealthResponse(BaseModel):
    """Response cho health check endpoint."""
    status: str = Field(default="healthy")
    documents_loaded: int = Field(default=0)
    chunks_indexed: int = Field(default=0)
    model: str = Field(default="")
    embedding_model: str = Field(default="")
