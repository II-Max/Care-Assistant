from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AI_SERVICE_DIR = PROJECT_ROOT / "ai-service"
sys.path.insert(0, str(AI_SERVICE_DIR))

from services.emergency_detector import emergency_detector
from rag.document_loader import DocumentLoader


def test_emergency_keyword_is_fail_safe():
    result = emergency_detector.detect("Bố tôi đang đau ngực dữ dội và khó thở")
    assert result["is_emergency"] is True
    assert result["level"] == "EMERGENCY"


def test_non_emergency_information_request_does_not_trigger_emergency():
    result = emergency_detector.detect("Bệnh viện mở cửa từ mấy giờ?")
    assert result["is_emergency"] is False


def test_legacy_loader_excludes_scraping_artifacts():
    data_dir = PROJECT_ROOT / "Data"
    docs = DocumentLoader(data_dir=str(data_dir)).load_all()
    artifact_prefixes = ("🏷️", "📇", "📊", "📋", "🔗", "🖼️")
    assert docs
    assert all(not doc.source_file.startswith(artifact_prefixes) for doc in docs)
