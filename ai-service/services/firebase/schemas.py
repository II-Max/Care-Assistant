"""
Firebase Firestore Data Models cho AI Customer Care.

Collections:
- conversations: Moit phien chat
- messages: Tin nhan trong conversation (subcollection)
- feedback: Danh gia cua nguoi dung
- audit_logs: Log an danh cho monitoring
- emergency_logs: Log su kien cap cuu
- users: Thong tin nguoi dung (co auth)
- bookings: Dat lich kham (Phase 3)
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Conversation:
    """Mot phien chat giua nguoi dung va AI."""
    conversation_id: str = ""
    user_id: Optional[str] = None
    user_ip: str = ""
    device_info: str = ""
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    message_count: int = 0
    risk_level: str = "LOW"
    emergency_triggered: bool = False
    handoff_requested: bool = False
    feedback_count: int = 0
    avg_confidence: float = 0.0
    is_active: bool = True

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "user_ip": self.user_ip[:100],
            "device_info": self.device_info[:100],
            "start_time": self.start_time,
            "end_time": self.end_time,
            "message_count": self.message_count,
            "risk_level": self.risk_level,
            "emergency_triggered": self.emergency_triggered,
            "handoff_requested": self.handoff_requested,
            "feedback_count": self.feedback_count,
            "avg_confidence": self.avg_confidence,
            "is_active": self.is_active,
        }


@dataclass
class Message:
    """Mot tin nhan trong conversation."""
    conversation_id: str
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    sources: list = field(default_factory=list)
    risk_level: str = "LOW"
    confidence: float = 0.0
    handoff_required: bool = False
    is_emergency: bool = False
    latency_ms: int = 0
    retrieval_scores: list = field(default_factory=list)
    chunks_used: int = 0
    feedback_rating: Optional[int] = None
    feedback_comment: Optional[str] = None
    feedback_time: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content[:5000],
            "timestamp": self.timestamp,
            "sources": self.sources,
            "risk_level": self.risk_level,
            "confidence": self.confidence,
            "handoff_required": self.handoff_required,
            "is_emergency": self.is_emergency,
            "latency_ms": self.latency_ms,
            "retrieval_scores": self.retrieval_scores,
            "chunks_used": self.chunks_used,
            "feedback_rating": self.feedback_rating,
            "feedback_comment": self.feedback_comment,
            "feedback_time": self.feedback_time,
        }


@dataclass
class Feedback:
    """Danh gia cau tra loi tu nguoi dung."""
    conversation_id: str
    message_id: str
    rating: int
    comment: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_ip: str = ""
    category: str = "general"

    def to_dict(self) -> dict:
        return {
            "conversation_id": self.conversation_id,
            "message_id": self.message_id,
            "rating": self.rating,
            "comment": self.comment[:500] if self.comment else "",
            "timestamp": self.timestamp,
            "user_ip": self.user_ip[:100],
            "category": self.category,
        }


@dataclass
class AuditLog:
    """Log an danh — khong chua PII."""
    event_type: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    conversation_id: Optional[str] = None
    risk_level: str = "LOW"
    confidence: float = 0.0
    latency_ms: int = 0
    retrieval_count: int = 0
    emergency_triggered: bool = False
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    user_ip_hash: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "conversation_id": self.conversation_id,
            "risk_level": self.risk_level,
            "confidence": self.confidence,
            "latency_ms": self.latency_ms,
            "retrieval_count": self.retrieval_count,
            "emergency_triggered": self.emergency_triggered,
            "error_type": self.error_type,
            "error_message": self.error_message[:500] if self.error_message else "",
            "user_ip_hash": self.user_ip_hash[:100],
            "metadata": self.metadata,
        }


@dataclass
class EmergencyLog:
    """Log su kien cap cuu de review."""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_message: str = ""
    matched_keywords: list = field(default_factory=list)
    response_sent: str = ""
    response_time_ms: int = 0
    conversation_id: Optional[str] = None
    user_ip_hash: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "user_message": self.user_message[:1000],
            "matched_keywords": self.matched_keywords,
            "response_sent": self.response_sent[:2000],
            "response_time_ms": self.response_time_ms,
            "conversation_id": self.conversation_id,
            "user_ip_hash": self.user_ip_hash[:100],
            "latitude": self.latitude,
            "longitude": self.longitude,
        }


@dataclass
class User:
    """Nguoi dung — khi co authentication."""
    user_id: str
    email: str = ""
    phone: str = ""
    display_name: str = ""
    role: str = "patient"
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    total_conversations: int = 0
    profile_complete: bool = False
    preferences: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "email": self.email,
            "phone": self.phone,
            "display_name": self.display_name,
            "role": self.role,
            "created_at": self.created_at,
            "last_active": self.last_active,
            "total_conversations": self.total_conversations,
            "profile_complete": self.profile_complete,
            "preferences": self.preferences,
        }


@dataclass
class Booking:
    """Dat lich kham (Phase 3)."""
    user_id: Optional[str] = None
    patient_name: str = ""
    patient_phone: str = ""
    patient_email: str = ""
    patient_dob: Optional[str] = None
    booking_date: str = ""
    booking_time: str = ""
    department: str = ""
    doctor_name: Optional[str] = None
    symptoms: str = ""
    notes: str = ""
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancelled_reason: Optional[str] = None
    idempotency_key: str = ""
    source: str = "ai_chat"

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "patient_name": self.patient_name,
            "patient_phone": self.patient_phone,
            "patient_email": self.patient_email,
            "patient_dob": self.patient_dob,
            "booking_date": self.booking_date,
            "booking_time": self.booking_time,
            "department": self.department,
            "doctor_name": self.doctor_name,
            "symptoms": self.symptoms[:2000],
            "notes": self.notes[:2000],
            "status": self.status,
            "created_at": self.created_at,
            "confirmed_at": self.confirmed_at,
            "cancelled_at": self.cancelled_at,
            "cancelled_reason": self.cancelled_reason,
            "idempotency_key": self.idempotency_key,
            "source": self.source,
        }
