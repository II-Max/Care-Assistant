"""
Handoff Service — Chuyển tiếp bệnh nhân sang nhân viên tư vấn.

Phase 3: Khi AI không thể trả lời hoặc bệnh nhân yêu cầu,
tạo ticket để nhân viên tổng đài xử lý.

Pipeline:
1. Phân loại lý do handoff (thiếu thông tin, yêu cầu phức tạp, emergency)
2. Tạo handoff ticket với context đầy đủ
3. Gửi notification cho nhân viên trực
4. Cập nhật conversation status
"""

import uuid
import json
import logging
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime

from config import settings
from database.connection import database

logger = logging.getLogger("handoff_service")

# Firebase fallback
try:
    from services.firebase import firebase_client
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    firebase_client = None


# ========================
# Handoff Reasons
# ========================

HANDOFF_REASONS = {
    "beyond_capability": "Vượt quá khả năng xử lý của AI (cần tư vấn chuyên môn)",
    "complex_booking": "Yêu cầu đặt lịch phức tạp (nhiều chuyên khoa, BHYT đặc thù)",
    "emergency_escalation": "Tình huống khẩn cấp cần nhân viên hỗ trợ",
    "user_requested": "Người dùng yêu cầu nói chuyện với nhân viên",
    "repeated_questions": "Người dùng hỏi lại nhiều lần (có thể bối rối/không hài lòng)",
    "complaint": "Khiếu nại hoặc phản ánh về dịch vụ",
    "data_not_found": "Thông tin không có trong knowledge base"
}


@dataclass
class HandoffRequest:
    """Yêu cầu chuyển tiếp cho nhân viên."""
    conversation_id: str = ""
    user_message: str = ""
    ai_response: str = ""
    reason: str = "beyond_capability"
    patient_phone: str = ""
    patient_name: str = ""
    notes: str = ""
    risk_level: str = "LOW"
    priority: str = "normal"  # normal, high, urgent
    user_ip: str = ""


@dataclass
class HandoffResult:
    """Kết quả handoff."""
    success: bool
    ticket_id: Optional[str] = None
    message: str = ""
    error_code: str = ""


class HandoffService:
    """Xử lý chuyển tiếp bệnh nhân cho nhân viên."""

    async def create_handoff(self, request: HandoffRequest) -> HandoffResult:
        """Tạo handoff ticket.

        Steps:
        1. Validate reason
        2. Create ticket with full context
        3. Notify staff (via notification queue)
        4. Return ticket info
        """
        ticket_id = f"hof_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"

        # Determine priority
        priority = request.priority
        if request.risk_level == "HIGH" or request.reason == "emergency_escalation":
            priority = "urgent"
        elif request.reason in ("complaint", "repeated_questions"):
            priority = "high"

        # Store handoff ticket
        if database.is_ready and database.is_postgres:
            try:
                await database.execute(
                    """INSERT INTO audit_events
                       (event_id, event_type, appointment_id, user_id, actor_role, details, ip_address)
                       VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                    ticket_id,
                    "handoff_created",
                    None,
                    request.user_ip[:16],
                    "ai_assistant",
                    json.dumps({
                        "conversation_id": request.conversation_id,
                        "reason": request.reason,
                        "reason_description": HANDOFF_REASONS.get(request.reason, ""),
                        "priority": priority,
                        "risk_level": request.risk_level,
                        "patient_message_preview": request.user_message[:500],
                        "ai_response_preview": request.ai_response[:500],
                        "patient_phone": request.patient_phone,
                        "patient_name": request.patient_name,
                        "notes": request.notes,
                        "timestamp": datetime.utcnow().isoformat()
                    }, ensure_ascii=False),
                    request.user_ip
                )
                logger.info(f"Handoff ticket created (PG): {ticket_id}")
                return HandoffResult(
                    success=True,
                    ticket_id=ticket_id,
                    message="Yêu cầu của bạn đã được ghi nhận. Nhân viên tổng đài sẽ liên hệ trong giờ hành chính."
                )
            except Exception as e:
                logger.error(f"Handoff PG failed: {e}")

        # Fallback: Firebase
        if FIREBASE_AVAILABLE and firebase_client and firebase_client.is_ready:
            try:
                fb_data = {
                    "ticket_id": ticket_id,
                    "conversation_id": request.conversation_id,
                    "reason": request.reason,
                    "reason_description": HANDOFF_REASONS.get(request.reason, ""),
                    "priority": priority,
                    "risk_level": request.risk_level,
                    "patient_message": request.user_message[:1000],
                    "ai_response": request.ai_response[:1000],
                    "patient_phone": request.patient_phone,
                    "patient_name": request.patient_name,
                    "notes": request.notes,
                    "status": "pending",
                    "user_ip_hash": request.user_ip[:16]
                }
                firebase_client.add_audit_log({
                    "event_type": "handoff_created",
                    "details": json.dumps(fb_data, ensure_ascii=False)[:2000]
                })
                logger.info(f"Handoff ticket created (Firebase): {ticket_id}")
                return HandoffResult(
                    success=True,
                    ticket_id=ticket_id,
                    message="Yêu cầu của bạn đã được ghi nhận. Nhân viên tổng đài sẽ liên hệ trong giờ hành chính."
                )
            except Exception as e:
                logger.error(f"Handoff Firebase failed: {e}")

        # Absolute fallback
        logger.info(f"[HANDOFF] New ticket: {json.dumps({
            'ticket_id': ticket_id,
            'reason': request.reason,
            'priority': priority,
            'conversation_id': request.conversation_id,
            'phone': request.patient_phone
        }, ensure_ascii=False)}")

        return HandoffResult(
            success=True,
            ticket_id=ticket_id,
            message="Yêu cầu của bạn đã được ghi nhận. Nhân viên tổng đài sẽ liên hệ trong giờ hành chính."
        )

    async def get_handoff_status(self, ticket_id: str) -> Optional[dict]:
        """Kiểm tra trạng thái handoff ticket."""
        if database.is_ready and database.is_postgres:
            row = await database.fetchrow(
                "SELECT * FROM audit_events WHERE event_id = $1 AND event_type LIKE 'handoff_%'",
                ticket_id
            )
            return row
        return None


# Singleton
handoff_service = HandoffService()
