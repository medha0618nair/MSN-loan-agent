"""
Lightweight KYC agent tests using stubs so they can run without OCR/vision dependencies.
"""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure the agent module is importable when tests run from repo root
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

import main  # noqa: E402
from ocr_utils import OCRProcessor
from file_utils import compute_sha256, validate_file_exists


client = TestClient(main.app)


def test_health_check():
    """Health endpoint returns the expected payload."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "kyc_agent"
    assert data["version"] == "kyc-v1"


class TestOCRProcessor:
    """Pure regex/heuristic OCR helpers (no external deps)."""

    @pytest.fixture
    def processor(self):
        return OCRProcessor()

    def test_pan_pattern(self, processor):
        text = "PAN Number: ABCDE1234F\nName: John Doe"
        result = processor.extract_pan(text)
        assert result["found"] is True
        assert result["pan_number"] == "ABCDE1234F"

    def test_email_and_phone(self, processor):
        text = "Contact: john.doe@example.com or 9876543210"
        result = processor.extract_contact_info(text)
        assert result["email_found"] is True
        assert result["phone_found"] is True

    def test_payslip_parsing(self, processor):
        text = "Gross Salary: Rs. 75,000.00\nNet Salary: Rs. 70,000.00"
        result = processor.parse_payslip(text)
        assert result["gross_salary"] == 75000.0
        assert result["amounts_found"]


class TestFileUtils:
    """File helpers that do not rely on external OCR libs."""

    def test_sha256_computation(self, tmp_path):
        sample = tmp_path / "test.txt"
        sample.write_text("hello")
        digest = compute_sha256(str(sample))
        assert len(digest) == 64
        assert digest != "error_computing_hash"

    def test_validate_file_exists(self, tmp_path):
        missing = tmp_path / "missing.pdf"
        assert validate_file_exists(str(missing)) is False

        existing = tmp_path / "exists.pdf"
        existing.write_text("hi")
        assert validate_file_exists(str(existing)) is True


class TestParseEndpoint:
    """Endpoint coverage with stubs to avoid heavy deps."""

    def test_pan_with_face_success(self, monkeypatch):
        monkeypatch.setattr(main, "validate_file_exists", lambda _: True)
        monkeypatch.setattr(main, "compute_sha256", lambda _: "deadbeef")

        monkeypatch.setattr(
            main.ocr_processor,
            "process_document",
            lambda _path, _doc: {
                "raw_text": "ABCDE1234F",
                "structured_fields": {"pan_number": "ABCDE1234F", "name": "Test User"},
                "confidence": 0.82,
                "text_length": 10,
            },
        )

        monkeypatch.setattr(
            main.face_detector,
            "detect_and_crop_face",
            lambda _path: (object(), (10, 20, 30, 40), 0.76),
        )
        monkeypatch.setattr(main, "save_face_crop", lambda _img, _path: True)

        payload = {
            "application_id": "app-123",
            "evidence_id": "ev-1",
            "doc_type": "pan",
            "file_path": "dummy.jpg",
        }

        resp = client.post("/kyc/parse", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        assert data["file_sha256"] == "deadbeef"
        assert data["overall_confidence"] == pytest.approx((0.82 + 0.76) / 2)
        assert data["ocr"]["structured_fields"]["pan_number"] == "ABCDE1234F"
        assert data["id_crop_evidence"]["face_detected"] is True
        assert data["validation_errors"] == []

    def test_pan_no_face_adds_validation(self, monkeypatch):
        monkeypatch.setattr(main, "validate_file_exists", lambda _: True)
        monkeypatch.setattr(main, "compute_sha256", lambda _: "deadbeef")
        monkeypatch.setattr(
            main.ocr_processor,
            "process_document",
            lambda _path, _doc: {
                "raw_text": "ABCDE1234F",
                "structured_fields": {"pan_number": "ABCDE1234F"},
                "confidence": 0.64,
                "text_length": 10,
            },
        )
        monkeypatch.setattr(main.face_detector, "detect_and_crop_face", lambda _path: (None, None, 0.0))

        payload = {
            "application_id": "app-456",
            "evidence_id": "ev-2",
            "doc_type": "pan",
            "file_path": "dummy.jpg",
        }

        resp = client.post("/kyc/parse", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        assert "Face not detected" in data["validation_errors"][0]
        assert data["id_crop_evidence"]["face_detected"] is False
        assert data["overall_confidence"] == pytest.approx(0.64)

    def test_missing_file_returns_404(self, monkeypatch):
        monkeypatch.setattr(main, "validate_file_exists", lambda _: False)

        payload = {
            "application_id": "app-789",
            "evidence_id": "ev-3",
            "doc_type": "payslip",
            "file_path": "missing.pdf",
        }

        resp = client.post("/kyc/parse", json=payload)
        assert resp.status_code == 404
        assert "File not found" in resp.json()["detail"]

    def test_aadhaar_missing_number_flags_validation(self, monkeypatch):
        monkeypatch.setattr(main, "validate_file_exists", lambda _: True)
        monkeypatch.setattr(main, "compute_sha256", lambda _: "hash")
        monkeypatch.setattr(
            main.ocr_processor,
            "process_document",
            lambda _path, _doc: {
                "raw_text": "AADHAAR HOLDER",
                "structured_fields": {"aadhaar_number": None},
                "confidence": 0.5,
                "text_length": 12,
            },
        )
        monkeypatch.setattr(main.face_detector, "detect_and_crop_face", lambda _path: (None, None, 0.0))

        payload = {
            "application_id": "app-aadhaar",
            "evidence_id": "ev-aadhaar",
            "doc_type": "aadhaar",
            "file_path": "aadhaar.jpg",
        }

        resp = client.post("/kyc/parse", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert any("Aadhaar number" in err for err in data["validation_errors"])

    def test_payslip_net_gt_gross_adds_validation(self, monkeypatch):
        monkeypatch.setattr(main, "validate_file_exists", lambda _: True)
        monkeypatch.setattr(main, "compute_sha256", lambda _: "hash")
        monkeypatch.setattr(
            main.ocr_processor,
            "process_document",
            lambda _path, _doc: {
                "raw_text": "Gross Salary: 50000 Net Salary: 60000",
                "structured_fields": {"gross_salary": 50000, "net_salary": 60000},
                "confidence": 0.6,
                "text_length": 30,
            },
        )
        monkeypatch.setattr(main.face_detector, "detect_and_crop_face", lambda _path: (None, None, 0.0))

        payload = {
            "application_id": "app-pay",
            "evidence_id": "ev-pay",
            "doc_type": "payslip",
            "file_path": "pay.pdf",
        }

        resp = client.post("/kyc/parse", json=payload)
        data = resp.json()
        assert any("Net salary exceeds" in err for err in data["validation_errors"])

    def test_bank_statement_needs_salary_signal(self, monkeypatch):
        monkeypatch.setattr(main, "validate_file_exists", lambda _: True)
        monkeypatch.setattr(main, "compute_sha256", lambda _: "hash")
        monkeypatch.setattr(
            main.ocr_processor,
            "process_document",
            lambda _path, _doc: {
                "raw_text": "Statement without payroll",
                "structured_fields": {"salary_hits": 0, "has_salary_signal": False},
                "confidence": 0.4,
                "text_length": 24,
            },
        )
        monkeypatch.setattr(main.face_detector, "detect_and_crop_face", lambda _path: (None, None, 0.0))

        payload = {
            "application_id": "app-bank",
            "evidence_id": "ev-bank",
            "doc_type": "bank_statement",
            "file_path": "bank.pdf",
        }

        resp = client.post("/kyc/parse", json=payload)
        data = resp.json()
        assert any("salary/payroll" in err for err in data["validation_errors"])
