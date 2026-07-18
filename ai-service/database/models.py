"""
PostgreSQL Data Models cho Care Assistant.

Bang:
- users: Nguoi dung (patient, doctor, admin)
- doctors: Bac si
- departments: Khoa phong
- schedules: Lich lam viec cua bac si
- time_slots: Cac khung gio trong ngay
- appointments: Dat lich kham
- appointment_histories: Lich su thay doi trang thai
- audit_events: Audit log
- notification_queue: Hang cho notification
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, date, time
from decimal import Decimal


# ========================
# Enums (string constants)
# ========================

class UserRole:
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"
    STAFF = "staff"


class AppointmentStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class NotificationChannel:
    ZALO = "zalo"
    SMS = "sms"
    EMAIL = "email"


class NotificationStatus:
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


# ========================
# Data Models
# ========================

@dataclass
class User:
    """Nguoi dung he thong."""
    user_id: str  # Firebase UID hoac UUID
    email: str = ""
    phone: str = ""
    display_name: str = ""
    role: str = UserRole.PATIENT
    id_card: str = ""  # CMND/CCCD (encrypted)
    bhyt_code: str = ""  # Ma BHYT
    dob: Optional[date] = None
    gender: str = ""
    address: str = ""
    profile_picture: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Serialize, loai bo PII neu can."""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "phone": self.phone,
            "display_name": self.display_name,
            "role": self.role,
            "bhyt_code": self.bhyt_code[-4:] if self.bhyt_code else "",
            "dob": self.dob.isoformat() if self.dob else None,
            "gender": self.gender,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }


@dataclass
class Doctor:
    """Thong tin bac si."""
    doctor_id: str
    user_id: str  # FK -> users
    department_id: str  # FK -> departments
    license_number: str = ""  # So chung chi hanh nghe
    specialization: str = ""
    title: str = ""  # TS, BS, ThS,...
    experience_years: int = 0
    bio: str = ""
    avatar_url: str = ""
    max_patients_per_day: int = 30
    is_accepting: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "doctor_id": self.doctor_id,
            "user_id": self.user_id,
            "department_id": self.department_id,
            "specialization": self.specialization,
            "title": self.title,
            "experience_years": self.experience_years,
            "bio": self.bio[:500],
            "max_patients_per_day": self.max_patients_per_day,
            "is_accepting": self.is_accepting,
        }


@dataclass
class Department:
    """Khoa phong benh vien."""
    department_id: str
    name: str
    description: str = ""
    location: str = ""
    phone: str = ""
    working_hours: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "department_id": self.department_id,
            "name": self.name,
            "description": self.description[:300],
            "location": self.location,
            "phone": self.phone,
            "working_hours": self.working_hours,
        }


@dataclass
class Schedule:
    """Lich lam viec cua bac si.

    Moi schedule la mot ngay lam viec voi danh sach time_slots.
    """
    schedule_id: str
    doctor_id: str  # FK -> doctors
    department_id: str  # FK -> departments
    work_date: date
    start_time: time
    end_time: time
    slot_duration_minutes: int = 15
    max_patients: int = 30
    is_available: bool = True
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "schedule_id": self.schedule_id,
            "doctor_id": self.doctor_id,
            "department_id": self.department_id,
            "work_date": self.work_date.isoformat(),
            "start_time": self.start_time.isoformat()[:5],
            "end_time": self.end_time.isoformat()[:5],
            "slot_duration_minutes": self.slot_duration_minutes,
            "max_patients": self.max_patients,
            "is_available": self.is_available,
        }


@dataclass
class TimeSlot:
    """Mot khung gio trong schedule.

    Vi du: schedule 08:00-11:30 -> slot 08:00, 08:15, 08:30, ...
    """
    slot_id: str
    schedule_id: str  # FK -> schedules
    doctor_id: str
    start_time: time
    end_time: time
    is_booked: bool = False
    booked_by: Optional[str] = None  # user_id
    booking_id: Optional[str] = None  # FK -> appointments
    version: int = 1  # Optimistic locking

    def to_dict(self) -> dict:
        return {
            "slot_id": self.slot_id,
            "schedule_id": self.schedule_id,
            "doctor_id": self.doctor_id,
            "start_time": self.start_time.isoformat()[:5],
            "end_time": self.end_time.isoformat()[:5],
            "is_booked": self.is_booked,
        }


@dataclass
class Appointment:
    """Mot cuoc hen kham benh."""
    appointment_id: str
    user_id: str  # FK -> users
    doctor_id: str  # FK -> doctors
    department_id: str  # FK -> departments
    slot_id: str  # FK -> time_slots
    schedule_id: str  # FK -> schedules

    # Thong tin benh nhan
    patient_name: str = ""
    patient_phone: str = ""
    patient_email: str = ""
    patient_dob: Optional[date] = None
    symptoms: str = ""
    notes: str = ""

    # Trang thai
    status: str = AppointmentStatus.PENDING
    check_in_time: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    cancel_reason: str = ""

    # Chi phi
    fee: Decimal = Decimal("0")
    is_bhyt: bool = False
    payment_status: str = "unpaid"
    payment_method: str = ""

    # Idempotency
    idempotency_key: str = ""

    # Metadata
    source: str = "ai_chat"
    reminder_sent: bool = False
    notification_channels: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "appointment_id": self.appointment_id,
            "user_id": self.user_id,
            "doctor_id": self.doctor_id,
            "department_id": self.department_id,
            "slot_id": self.slot_id,
            "patient_name": self.patient_name,
            "patient_phone": self.patient_phone[-4:],  # Che so cuoi
            "patient_dob": self.patient_dob.isoformat() if self.patient_dob else None,
            "symptoms": self.symptoms[:500],
            "notes": self.notes[:500],
            "status": self.status,
            "is_bhyt": self.is_bhyt,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class AppointmentHistory:
    """Lich su thay doi trang thai appointment."""
    history_id: str
    appointment_id: str
    new_status: str
    changed_by: str  # user_id
    previous_status: Optional[str] = None
    reason: str = ""
    ip_address: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AuditEvent:
    """Audit log cho booking operations."""
    event_id: str
    event_type: str  # booking_created, booking_cancelled, payment_received, ...
    appointment_id: Optional[str] = None
    user_id: Optional[str] = None
    actor_role: str = ""
    details: dict = field(default_factory=dict)
    ip_address: str = ""
    user_agent: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class NotificationQueue:
    """Hang cho gui notification (Zalo/SMS/Email)."""
    notification_id: str
    appointment_id: str
    channel: str  # zalo, sms, email
    recipient: str  # phone number hoac email
    template: str = ""
    params: dict = field(default_factory=dict)
    status: str = NotificationStatus.PENDING
    sent_at: Optional[datetime] = None
    error_message: str = ""
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.utcnow)
