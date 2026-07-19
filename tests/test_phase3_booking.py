import sys
from pathlib import Path
import pytest
import anyio
from datetime import date, timedelta

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AI_SERVICE_DIR = PROJECT_ROOT / "ai-service"
sys.path.insert(0, str(AI_SERVICE_DIR))

from services.booking_service import (
    BookingRequest, BookingResult, BookingService,
    validate_booking_request, DEPARTMENTS
)
from services.handoff_service import HandoffRequest, HandoffService


# ========================
# Booking Validation
# ========================

class TestBookingValidation:
    """Test validate_booking_request function."""

    def test_valid_booking(self):
        req = BookingRequest(
            patient_name="Nguyễn Văn A",
            patient_phone="0912345678",
            department_id="noi-khoa",
            booking_date=str(date.today() + timedelta(days=1)),
            booking_time="08:00",
            symptoms="Đau ngực trái"
        )
        error = validate_booking_request(req)
        assert error is None, f"Expected no error, got: {error}"

    def test_missing_name(self):
        req = BookingRequest(
            patient_name="A",
            patient_phone="0912345678",
            department_id="noi-khoa",
            booking_date=str(date.today() + timedelta(days=1)),
            booking_time="08:00"
        )
        error = validate_booking_request(req)
        assert error is not None
        assert "họ tên" in error.lower()

    def test_invalid_phone(self):
        req = BookingRequest(
            patient_name="Nguyễn Văn A",
            patient_phone="123",
            department_id="noi-khoa",
            booking_date=str(date.today() + timedelta(days=1)),
            booking_time="08:00"
        )
        error = validate_booking_request(req)
        assert error is not None
        assert "số điện thoại" in error.lower()

    def test_past_date(self):
        req = BookingRequest(
            patient_name="Nguyễn Văn A",
            patient_phone="0912345678",
            department_id="noi-khoa",
            booking_date=str(date.today() - timedelta(days=1)),
            booking_time="08:00"
        )
        error = validate_booking_request(req)
        assert error is not None
        assert "quá khứ" in error.lower()

    def test_too_far_future(self):
        req = BookingRequest(
            patient_name="Nguyễn Văn A",
            patient_phone="0912345678",
            department_id="noi-khoa",
            booking_date=str(date.today() + timedelta(days=60)),
            booking_time="08:00"
        )
        error = validate_booking_request(req)
        assert error is not None
        assert "30 ngày" in error.lower()

    def test_missing_department(self):
        req = BookingRequest(
            patient_name="Nguyễn Văn A",
            patient_phone="0912345678",
            department_id="",
            booking_date=str(date.today() + timedelta(days=1)),
            booking_time="08:00"
        )
        error = validate_booking_request(req)
        assert error is not None
        assert "chuyên khoa" in error.lower()


# ========================
# Departments Data
# ========================

class TestDepartments:
    """Test departments listing."""

    def test_departments_count(self):
        assert len(DEPARTMENTS) == 7

    def test_departments_have_required_fields(self):
        for dept in DEPARTMENTS:
            assert "id" in dept
            assert "name" in dept
            assert "description" in dept
            assert dept["id"], f"Department {dept.get('name', '?')} has empty id"

    def test_department_ids_unique(self):
        ids = [d["id"] for d in DEPARTMENTS]
        assert len(ids) == len(set(ids)), "Duplicate department IDs found"


# ========================
# Handoff Service
# ========================

class TestHandoffValidation:
    """Test handoff request validation."""

    def test_valid_handoff_request(self):
        """Handoff request creation should work with valid data."""
        req = HandoffRequest(
            conversation_id="conv_test_123",
            user_message="Tôi cần tư vấn thêm về bảo hiểm",
            ai_response="Xin lỗi, tôi chưa có thông tin này",
            reason="beyond_capability",
            risk_level="LOW"
        )
        # Only test creation, not DB persistence
        assert req.reason == "beyond_capability"
        assert req.risk_level == "LOW"
        assert req.conversation_id == "conv_test_123"

    def test_handoff_risk_levels(self):
        """Should accept all valid risk levels."""
        valid_levels = ["LOW", "MEDIUM", "HIGH", "EMERGENCY"]
        for level in valid_levels:
            req = HandoffRequest(
                conversation_id="conv_test",
                user_message="test",
                ai_response="test",
                reason="beyond_capability",
                risk_level=level
            )
            assert req.risk_level == level


# ========================
# Booking Service (unit tests, no DB)
# ========================

async def _test_get_appointment_no_db():
    """Should return None when database is not initialized."""
    service = BookingService()
    result = await service.get_appointment("nonexistent")
    assert result is None


async def _test_get_appointments_by_phone_no_db():
    """Should return empty list when database is not initialized."""
    service = BookingService()
    result = await service.get_appointments_by_phone("0912345678")
    assert result == []


async def _test_cancel_appointment_no_db():
    """Should return error when database is not initialized."""
    service = BookingService()
    result = await service.cancel_appointment("nonexistent")
    assert result.success is False


class TestBookingServiceAsync:
    """Test booking service methods that don't require DB (via anyio)."""

    def test_get_appointment_no_db(self):
        anyio.run(_test_get_appointment_no_db)

    def test_get_appointments_by_phone_no_db(self):
        anyio.run(_test_get_appointments_by_phone_no_db)

    def test_cancel_appointment_no_db(self):
        anyio.run(_test_cancel_appointment_no_db)
