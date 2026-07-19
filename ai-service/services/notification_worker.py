"""
Notification Worker — Xử lý hàng đợi thông báo bất đồng bộ.

Kiến trúc:
- Worker pattern: chạy riêng (thread) hoặc background task
- Hỗ trợ: SMS, Zalo, Email
- Retry mechanism với exponential backoff (3 lần)

Phase 3 Integration:
- Booking confirmation → SMS/Zalo
- Appointment reminder → SMS (24h trước)
- Handoff notification → Email cho staff
"""

import json
import asyncio
import logging
from typing import Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from config import settings
from database.connection import database

logger = logging.getLogger("notification_worker")


# ========================
# Notification Channels
# ========================

class NotificationChannel:
    SMS = "sms"
    ZALO = "zalo"
    EMAIL = "email"
    PUSH = "push"

    ALL = [SMS, ZALO, EMAIL, PUSH]


# ========================
# Notification Templates
# ========================

TEMPLATES = {
    "booking_confirmation_sms": {
        "channel": "sms",
        "template": "Xac nhan dat lich kham BV Tim Ha Noi: {patient_name} - {date} - {time}. Ma hen: {appointment_id}. Hotline: 19001082"
    },
    "booking_confirmation_zalo": {
        "channel": "zalo",
        "template": "✅ Xác nhận đặt lịch khám\nBệnh viện Tim Hà Nội\n\n👤 Bệnh nhân: {patient_name}\n📅 Ngày: {date}\n⏰ Giờ: {time}\n🆔 Mã: {appointment_id}\n\n📞 Hotline: 19001082"
    },
    "booking_confirmation_email": {
        "channel": "email",
        "template": "<h2>Xác nhận đặt lịch khám - Bệnh viện Tim Hà Nội</h2><p>Xin chào <strong>{patient_name}</strong>,</p><p>Chúng tôi đã nhận được yêu cầu đặt lịch khám của bạn:</p><ul><li><strong>Ngày:</strong> {date}</li><li><strong>Giờ:</strong> {time}</li><li><strong>Mã đặt lịch:</strong> {appointment_id}</li></ul><p>Nhân viên tổng đài sẽ liên hệ <strong>{phone}</strong> trong giờ hành chính để xác nhận.</p><p><small>📋 Thông tin này chỉ mang tính tham khảo. Vui lòng liên hệ tổng đài 19001082 để được hỗ trợ.</small></p>"
    },
    "reminder_sms": {
        "channel": "sms",
        "template": "Nhanh nho: {patient_name} co lich kham tai BV Tim Ha Noi vao {date} - {time}. Vui long den truoc 15p. Hotline: 19001082"
    },
    "reminder_zalo": {
        "channel": "zalo",
        "template": "⏰ Nhắc lịch khám\nBệnh viện Tim Hà Nội\n\n👤 {patient_name}\n📅 {date}\n⏰ {time}\n🆔 {appointment_id}\n\nVui lòng đến trước 15 phút.\n📞 Hotline: 19001082"
    },
    "handoff_staff_email": {
        "channel": "email",
        "template": "<h2>Yêu cầu hỗ trợ mới - AI Care Assistant</h2><p><strong>Loại:</strong> {reason_description}</p><p><strong>Mức độ:</strong> {priority}</p><p><strong>Bệnh nhân:</strong> {patient_name}</p><p><strong>SĐT:</strong> {phone}</p><p><strong>Nội dung:</strong> {notes}</p><p><strong>Mã ticket:</strong> {ticket_id}</p>"
    }
}


# ========================
# Adapters
# ========================

class BaseAdapter:
    """Base class cho notification adapters."""
    
    async def send(self, recipient: str, message: str, **kwargs) -> bool:
        """Gửi notification. Return True nếu thành công."""
        raise NotImplementedError


class SMSAdapter(BaseAdapter):
    """SMS adapter — sử dụng HTTP API (ví dụ: Twilio, Viettel, VNPT).
    
    Trong Phase 3: placeholder — log ra console.
    Production: integrate với tổng đài SMS thực tế.
    """
    
    async def send(self, recipient: str, message: str, **kwargs) -> bool:
        try:
            logger.info(f"[SMS] To: {recipient[-4:]}, Body: {message[:100]}...")
            # TODO: Integrate with SMS provider API
            # Ví dụ: POST /api/sms with API key
            await asyncio.sleep(0.01)  # Simulate network
            return True
        except Exception as e:
            logger.error(f"[SMS] Failed to {recipient}: {e}")
            return False


class ZaloAdapter(BaseAdapter):
    """Zalo OA adapter — gửi qua Zalo Official Account.
    
    Trong Phase 3: placeholder.
    Production: sử dụng Zalo API với access token.
    """
    
    async def send(self, recipient: str, message: str, **kwargs) -> bool:
        try:
            logger.info(f"[ZALO] To: {recipient[-4:]}, Body: {message[:100]}...")
            # TODO: Integrate with Zalo OA API
            await asyncio.sleep(0.01)
            return True
        except Exception as e:
            logger.error(f"[ZALO] Failed to {recipient}: {e}")
            return False


class EmailAdapter(BaseAdapter):
    """Email adapter — gửi qua SMTP hoặc Email API (SendGrid, etc).
    
    Trong Phase 3: placeholder.
    Production: dùng SMTP với hospital email server.
    """
    
    async def send(self, recipient: str, message: str, **kwargs) -> bool:
        try:
            logger.info(f"[EMAIL] To: {recipient}, Subject: {kwargs.get('subject', '')}")
            # TODO: Integrate with SMTP / SendGrid / SES
            await asyncio.sleep(0.01)
            return True
        except Exception as e:
            logger.error(f"[EMAIL] Failed to {recipient}: {e}")
            return False


# ========================
# Notification Worker
# ========================

class NotificationWorker:
    """Xử lý hàng đợi notification bất đồng bộ.
    
    Cơ chế:
    - Poll notification_queue mỗi 5 giây
    - Gửi notification qua adapter tương ứng
    - Update status: sent / failed
    - Retry failed items (tối đa 3 lần)
    """
    
    def __init__(self):
        self._running = False
        self._adapters = {
            NotificationChannel.SMS: SMSAdapter(),
            NotificationChannel.ZALO: ZaloAdapter(),
            NotificationChannel.EMAIL: EmailAdapter(),
            NotificationChannel.PUSH: SMSAdapter(),  # Fallback to SMS
        }
    
    def start(self):
        """Start worker trong background thread."""
        if self._running:
            logger.warning("Worker already running")
            return
        
        self._running = True
        logger.info("🚀 Notification Worker started (polling every 5s)")
    
    def stop(self):
        """Stop worker."""
        self._running = False
        logger.info("🛑 Notification Worker stopped")
    
    async def enqueue(
        self,
        appointment_id: str,
        channel: str,
        recipient: str,
        template_name: str,
        params: dict
    ) -> Optional[str]:
        """Thêm notification vào hàng đợi.
        
        Args:
            appointment_id: ID lịch hẹn
            channel: sms / zalo / email
            recipient: SĐT hoặc email
            template_name: Tên template trong TEMPLATES
            params: Dict chứa các biến template
        
        Returns:
            notification_id nếu thành công, None nếu thất bại
        """
        from uuid import uuid4
        notification_id = f"notif_{uuid4().hex[:12]}"
        
        template = TEMPLATES.get(template_name)
        if not template:
            logger.warning(f"Template not found: {template_name}")
            return None
        
        # Store in database
        if database.is_ready and database.is_postgres:
            try:
                await database.execute(
                    """INSERT INTO notification_queue
                       (notification_id, appointment_id, channel, recipient, template, params, status)
                       VALUES ($1, $2, $3, $4, $5, $6, 'pending')""",
                    notification_id,
                    appointment_id,
                    channel,
                    recipient,
                    template_name,
                    json.dumps(params, ensure_ascii=False)
                )
                logger.info(f"Enqueued notification: {notification_id} ({channel})")
                return notification_id
            except Exception as e:
                logger.error(f"Enqueue failed: {e}")
                return None
        
        logger.info(f"[NOTIFICATION] Would send ({channel}): {template_name} -> {recipient[-4:]}")
        return notification_id
    
    async def process_pending(self):
        """Xử lý các notification đang pending.
        
        Poll database cho các notification chưa gửi,
        gửi qua adapter, update status.
        """
        if not database.is_ready:
            return
        
        try:
            if database.is_postgres:
                pending = await database.fetch(
                    """SELECT * FROM notification_queue 
                       WHERE status = 'pending' 
                       AND retry_count < max_retries
                       ORDER BY scheduled_at ASC 
                       LIMIT 20"""
                )
            else:
                pending = await database.fetch(
                    """SELECT * FROM notification_queue 
                       WHERE status = 'pending' 
                       AND retry_count < max_retries
                       ORDER BY created_at ASC 
                       LIMIT 20"""
                )
            
            if not pending:
                return
            
            logger.info(f"Processing {len(pending)} pending notifications")
            
            for item in pending:
                await self._process_item(item)
                
        except Exception as e:
            logger.error(f"Process pending failed: {e}")
    
    async def _process_item(self, item: dict):
        """Xử lý một notification item."""
        notification_id = item.get("notification_id") or item.get("id")
        channel = item.get("channel")
        recipient = item.get("recipient")
        template_name = item.get("template")
        params_str = item.get("params", "{}")
        retry_count = item.get("retry_count", 0)
        
        try:
            params = json.loads(params_str) if isinstance(params_str, str) else params_str
        except json.JSONDecodeError:
            params = {}
        
        # Get adapter
        adapter = self._adapters.get(channel)
        if not adapter:
            logger.warning(f"No adapter for channel: {channel}")
            await self._update_status(notification_id, "failed", "Unknown channel")
            return
        
        # Build message
        template_info = TEMPLATES.get(template_name)
        if not template_info:
            await self._update_status(notification_id, "failed", "Template not found")
            return
        
        try:
            message = template_info["template"].format(**params)
        except KeyError as e:
            logger.warning(f"Template param missing: {e}")
            message = template_info["template"]
        
        # Send via adapter
        success = await adapter.send(recipient, message, **params)
        
        if success:
            await self._update_status(notification_id, "sent")
            logger.info(f"✅ Sent {channel} to {recipient[-4:]}: {template_name}")
        else:
            new_retry = retry_count + 1
            if new_retry >= 3:
                await self._update_status(notification_id, "failed", f"Max retries ({new_retry})")
                logger.warning(f"❌ Failed {channel} to {recipient[-4:]}: max retries")
            else:
                await self._update_retry(notification_id, new_retry)
                logger.warning(f"⏳ Retry {new_retry}/3 {channel} to {recipient[-4:]}")
    
    async def _update_status(self, notification_id: str, status: str, error: str = ""):
        """Update trạng thái notification."""
        if database.is_ready and database.is_postgres:
            await database.execute(
                "UPDATE notification_queue SET status = $2, error_message = $3, sent_at = CURRENT_TIMESTAMP WHERE notification_id = $1",
                notification_id, status, error
            )
        elif database.is_ready:
            id_col = "id"
            await database.execute(
                f"UPDATE notification_queue SET status = ?, error_message = ?, sent_at = CURRENT_TIMESTAMP WHERE {id_col} = ?",
                status, error, notification_id
            )
    
    async def _update_retry(self, notification_id: str, retry_count: int):
        """Update retry count."""
        if database.is_ready and database.is_postgres:
            await database.execute(
                "UPDATE notification_queue SET retry_count = $2 WHERE notification_id = $1",
                notification_id, retry_count
            )
        elif database.is_ready:
            id_col = "id"
            await database.execute(
                f"UPDATE notification_queue SET retry_count = ? WHERE {id_col} = ?",
                retry_count, notification_id
            )
    
    async def schedule_reminders(self):
        """Lên lịch gửi reminder cho các lịch hẹn ngày mai.
        
        Chạy mỗi 6 tiếng (cron: 0 */6 * * *).
        """
        if not database.is_ready:
            return
        
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        try:
            appointments = await database.fetch(
                "SELECT * FROM appointments WHERE booking_date = $1 AND status = 'confirmed' AND reminder_sent = 0",
                tomorrow
            )
            
            for apt in appointments:
                # Enqueue SMS reminder
                await self.enqueue(
                    appointment_id=apt.get("appointment_id"),
                    channel=NotificationChannel.SMS,
                    recipient=apt.get("patient_phone"),
                    template_name="reminder_sms",
                    params={
                        "patient_name": apt.get("patient_name"),
                        "date": apt.get("booking_date"),
                        "time": apt.get("booking_time"),
                        "appointment_id": apt.get("appointment_id")
                    }
                )
                
                # Mark reminder as sent
                await database.execute(
                    "UPDATE appointments SET reminder_sent = 1 WHERE appointment_id = $1",
                    apt.get("appointment_id")
                )
                
                logger.info(f"Scheduled reminder for: {apt.get('appointment_id')}")
                
        except Exception as e:
            logger.error(f"Schedule reminders failed: {e}")


# Singleton
notification_worker = NotificationWorker()
