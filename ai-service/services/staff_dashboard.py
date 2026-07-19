"""
Staff Dashboard Service — Giao diện quản lý cho nhân viên tổng đài.

Phase 3: Cho phép nhân viên xem và quản lý handoff tickets,
booking requests, và emergency alerts.

Tính năng:
- Xem danh sách handoff tickets (pending, in_progress, resolved)
- Xem booking requests cần xác nhận
- Xem emergency alerts gần đây
- Cập nhật trạng thái ticket
- Ghi chú nội bộ
"""

import json
import uuid
import logging
from typing import Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from config import settings
from database.connection import database

logger = logging.getLogger("staff_dashboard")


# ========================
# Data Models
# ========================

@dataclass
class DashboardStats:
    """Thống kê tổng quan cho dashboard."""
    pending_handoffs: int = 0
    today_bookings: int = 0
    pending_bookings: int = 0
    emergency_alerts_24h: int = 0
    total_conversations_today: int = 0
    avg_confidence: float = 0.0
    avg_response_time_ms: int = 0


@dataclass
class HandoffTicket:
    """Một handoff ticket cho nhân viên xử lý."""
    ticket_id: str
    reason: str
    reason_description: str = ""
    priority: str = "normal"  # normal, high, urgent
    risk_level: str = "LOW"
    status: str = "pending"  # pending, in_progress, resolved, closed
    conversation_id: str = ""
    patient_name: str = ""
    patient_phone: str = ""
    user_message: str = ""
    ai_response: str = ""
    notes: str = ""
    assigned_to: str = ""
    resolution: str = ""
    created_at: str = ""
    updated_at: str = ""
    resolved_at: Optional[str] = None


@dataclass
class BookingRequest_Staff:
    """Đơn đặt lịch cần xử lý."""
    appointment_id: str
    patient_name: str = ""
    patient_phone: str = ""
    department_id: str = ""
    department_name: str = ""
    booking_date: str = ""
    booking_time: str = ""
    status: str = "pending"
    symptoms: str = ""
    is_bhyt: bool = False
    source: str = "ai_chat"
    created_at: str = ""
    confirmed_at: Optional[str] = None
    cancel_reason: str = ""


# ========================
# Staff Dashboard Service
# ========================

class StaffDashboard:
    """Service cung cấp dữ liệu cho staff dashboard."""

    async def get_stats(self) -> DashboardStats:
        """Lấy thống kê tổng quan."""
        stats = DashboardStats()
        
        if not database.is_ready:
            return stats
        
        try:
            # Pending handoffs (from audit_events)
            if database.is_postgres:
                row = await database.fetchrow(
                    "SELECT COUNT(*) as count FROM audit_events WHERE event_type = 'handoff_created'"
                )
                if row:
                    stats.pending_handoffs = row["count"]
                
                # Today's bookings
                today = datetime.now().strftime("%Y-%m-%d")
                row = await database.fetchrow(
                    "SELECT COUNT(*) as count FROM appointments WHERE booking_date = $1",
                    today
                )
                if row:
                    stats.today_bookings = row["count"]
                
                # Pending bookings
                row = await database.fetchrow(
                    "SELECT COUNT(*) as count FROM appointments WHERE status = 'pending'"
                )
                if row:
                    stats.pending_bookings = row["count"]
            else:
                # SQLite fallback queries
                today = datetime.now().strftime("%Y-%m-%d")
                rows = await database.fetch(
                    "SELECT COUNT(*) as count FROM appointments WHERE date(booking_date) = date(?)",
                    today
                )
                if rows:
                    stats.today_bookings = rows[0]["count"] if rows[0]["count"] else 0
                
                rows = await database.fetch(
                    "SELECT COUNT(*) as count FROM appointments WHERE status = 'pending'"
                )
                if rows:
                    stats.pending_bookings = rows[0]["count"] if rows[0]["count"] else 0
            
        except Exception as e:
            logger.error(f"Get stats failed: {e}")
        
        return stats

    async def get_handoff_tickets(
        self,
        status: str = "pending",
        limit: int = 50
    ) -> list[dict]:
        """Lấy danh sách handoff tickets."""
        tickets = []
        
        if not database.is_ready:
            return tickets
        
        try:
            # Get handoff events from audit_logs
            if database.is_postgres:
                rows = await database.fetch(
                    """SELECT * FROM audit_events 
                       WHERE event_type = 'handoff_created' 
                       ORDER BY created_at DESC 
                       LIMIT $1""",
                    limit
                )
            else:
                rows = await database.fetch(
                    """SELECT * FROM audit_events 
                       WHERE event_type = 'handoff_created' 
                       ORDER BY created_at DESC 
                       LIMIT ?""",
                    limit
                )
            
            for row in rows:
                details = {}
                details_str = row.get("details", "{}")
                if isinstance(details_str, str):
                    try:
                        details = json.loads(details_str)
                    except json.JSONDecodeError:
                        details = {}
                
                tickets.append({
                    "ticket_id": row.get("event_id"),
                    "conversation_id": details.get("conversation_id", ""),
                    "reason": details.get("reason", ""),
                    "reason_description": details.get("reason_description", ""),
                    "priority": details.get("priority", "normal"),
                    "risk_level": details.get("risk_level", "LOW"),
                    "patient_name": details.get("patient_name", ""),
                    "patient_phone": details.get("patient_phone", ""),
                    "user_message": details.get("patient_message_preview", ""),
                    "ai_response": details.get("ai_response_preview", ""),
                    "notes": details.get("notes", ""),
                    "status": "pending",  # Simplified — all handoff_created are pending
                    "created_at": str(row.get("created_at", "")),
                })
                
        except Exception as e:
            logger.error(f"Get handoff tickets failed: {e}")
        
        return tickets

    async def get_pending_bookings(self, limit: int = 50) -> list[dict]:
        """Lấy danh sách booking cần xác nhận."""
        bookings = []
        
        if not database.is_ready:
            return bookings
        
        try:
            # Map department IDs to names
            dept_map = {
                "noi-khoa": "Nội khoa Tim mạch",
                "can-thiep": "Tim mạch Can thiệp",
                "phau-thuat": "Phẫu thuật Tim mạch",
                "nhi-khoa": "Nhi khoa Tim mạch",
                "chuyen-hoa": "Tim mạch Chuyển hóa",
                "duoc": "Khoa Dược & Hiệu thuốc",
                "tong-quat": "Khám bệnh Tổng quát"
            }
            
            if database.is_postgres:
                id_col = "appointment_id"
                rows = await database.fetch(
                    f"""SELECT * FROM appointments 
                       WHERE status = 'pending' 
                       ORDER BY created_at DESC 
                       LIMIT $1""",
                    limit
                )
            else:
                id_col = "id"
                rows = await database.fetch(
                    f"""SELECT *, {id_col} as appointment_id FROM appointments 
                       WHERE status = 'pending' 
                       ORDER BY created_at DESC 
                       LIMIT ?""",
                    limit
                )
            
            for row in rows:
                dept_id = row.get("department_id", "")
                bookings.append({
                    "appointment_id": row.get(id_col) or row.get("appointment_id"),
                    "patient_name": row.get("patient_name", ""),
                    "patient_phone": row.get("patient_phone", ""),
                    "department_id": dept_id,
                    "department_name": dept_map.get(dept_id, dept_id),
                    "booking_date": str(row.get("booking_date", "")),
                    "booking_time": str(row.get("booking_time", "")),
                    "status": row.get("status", "pending"),
                    "symptoms": row.get("symptoms", ""),
                    "is_bhyt": bool(row.get("is_bhyt", False)),
                    "source": row.get("source", "ai_chat"),
                    "created_at": str(row.get("created_at", "")),
                })
                
        except Exception as e:
            logger.error(f"Get pending bookings failed: {e}")
        
        return bookings

    async def confirm_booking(self, appointment_id: str) -> dict:
        """Xác nhận booking từ staff dashboard."""
        if not database.is_ready:
            return {"success": False, "message": "Database chưa sẵn sàng."}
        
        try:
            id_col = "appointment_id" if database.is_postgres else "id"
            await database.execute(
                f"UPDATE appointments SET status = 'confirmed', updated_at = CURRENT_TIMESTAMP WHERE {id_col} = $1",
                appointment_id
            )
            
            # Schedule notification
            from services.notification_worker import notification_worker
            
            # Get appointment details for notification
            row = await database.fetchrow(
                f"SELECT * FROM appointments WHERE {id_col} = $1",
                appointment_id
            )
            
            if row:
                await notification_worker.enqueue(
                    appointment_id=appointment_id,
                    channel="sms",
                    recipient=row.get("patient_phone", ""),
                    template_name="booking_confirmation_sms",
                    params={
                        "patient_name": row.get("patient_name", ""),
                        "date": str(row.get("booking_date", "")),
                        "time": str(row.get("booking_time", "")),
                        "appointment_id": appointment_id
                    }
                )
            
            return {
                "success": True,
                "message": "Đã xác nhận lịch hẹn.",
                "appointment_id": appointment_id
            }
            
        except Exception as e:
            logger.error(f"Confirm booking failed: {e}")
            return {"success": False, "message": "Lỗi xác nhận."}

    async def resolve_handoff(
        self, ticket_id: str, resolution: str, assigned_to: str = ""
    ) -> dict:
        """Đánh dấu handoff đã xử lý."""
        if not database.is_ready:
            return {"success": False, "message": "Database chưa sẵn sàng."}
        
        try:
            # Update audit event with resolution
            details = json.dumps({
                "resolution": resolution,
                "assigned_to": assigned_to,
                "resolved_at": datetime.utcnow().isoformat()
            }, ensure_ascii=False)
            
            await database.execute(
                "UPDATE audit_events SET details = $2 WHERE event_id = $1",
                ticket_id, details
            )
            
            return {
                "success": True,
                "message": "Đã cập nhật ticket.",
                "ticket_id": ticket_id
            }
            
        except Exception as e:
            logger.error(f"Resolve handoff failed: {e}")
            return {"success": False, "message": "Lỗi cập nhật."}


# Singleton
staff_dashboard = StaffDashboard()
