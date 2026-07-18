import pytest
from services.emergency_detector import emergency_detector

def test_emergency_keywords():
    """Test Layer 1 Fail-safe for Emergency Detector."""
    
    # Những câu chứa keyword phải trả về EMERGENCY lập tức
    emergency_cases = [
        "Tôi bị đau ngực dữ dội",
        "Có người ngất xỉu",
        "Bệnh nhân đang hôn mê",
        "Tôi không thở được",
        "Đau đầu dữ dội quá"
    ]
    
    for case in emergency_cases:
        result = emergency_detector.detect(case)
        assert result["is_emergency"] is True
        assert result["level"] == "EMERGENCY"
        assert len(result["matched_keywords"]) > 0

def test_normal_queries():
    """Test normal questions do not trigger emergency."""
    
    normal_cases = [
        "Bệnh viện có khám BHYT không?",
        "Xin lịch làm việc của bác sĩ",
        "Tôi muốn đặt lịch khám",
        "Bệnh viện ở đâu?"
    ]
    
    for case in normal_cases:
        result = emergency_detector.detect(case)
        assert result["is_emergency"] is False
        assert result["level"] == "NORMAL"
        assert len(result["matched_keywords"]) == 0
