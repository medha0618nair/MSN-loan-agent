"""
Unit tests for face verification agent.
Tests: matching faces, non-matching faces, no-face errors, embedding storage.
"""

import pytest
import numpy as np
import cv2
from pathlib import Path
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from face_utils import FaceUtils
from liveness import LivenessDetector
from db import EmbeddingDB
from main import (
    verify_face,
    FaceVerificationRequest,
    EvidenceInput
)


class TestFaceUtils:
    """Test face detection and embedding generation."""
    
    def test_compute_similarity_identical_embeddings(self):
        """Test that identical embeddings have high similarity."""
        embedding = np.random.randn(512)
        similarity = FaceUtils.compute_similarity(embedding, embedding)
        assert similarity == pytest.approx(1.0, abs=0.01)
    
    def test_compute_similarity_different_embeddings(self):
        """Test that different embeddings have lower similarity."""
        embedding1 = np.random.randn(512)
        embedding2 = np.random.randn(512)
        similarity = FaceUtils.compute_similarity(embedding1, embedding2)
        assert 0.0 <= similarity <= 1.0
        assert similarity < 0.8  # Random embeddings should be dissimilar
    
    def test_compute_similarity_opposite_embeddings(self):
        """Test similarity with opposite embeddings."""
        embedding = np.ones(512)
        opposite = -np.ones(512)
        similarity = FaceUtils.compute_similarity(embedding, opposite)
        assert similarity < 0.3  # Should be low
    
    def test_load_image_nonexistent_file(self):
        """Test loading an image that doesn't exist."""
        result = FaceUtils.load_image("./nonexistent/image.jpg")
        assert result is None
    
    @patch('face_utils.cv2.imread')
    def test_load_image_failure(self, mock_imread):
        """Test handling of image load failure."""
        mock_imread.return_value = None
        result = FaceUtils.load_image("./test.jpg")
        assert result is None
    
    @patch('face_utils.FaceUtils.detect_face')
    def test_process_image_no_face_detected(self, mock_detect):
        """Test processing when no face is detected."""
        mock_detect.return_value = None
        result = FaceUtils.process_image_and_get_embedding("./test.jpg")
        assert result is None


class TestLivenessDetector:
    """Test liveness detection."""
    
    def test_euclidean_distance(self):
        """Test Euclidean distance calculation."""
        point1 = np.array([0, 0])
        point2 = np.array([3, 4])
        distance = LivenessDetector.euclidean_distance(point1, point2)
        assert distance == pytest.approx(5.0)
    
    def test_eye_aspect_ratio_open_eye(self):
        """Test EAR calculation for open eye."""
        # Simulated open eye landmarks
        eye_landmarks = np.array([
            [0, 0],    # left corner
            [2, 3],    # top-left
            [2, 3],    # top-right
            [4, 0],    # right corner
            [2, -3],   # bottom-right
            [2, -3]    # bottom-left
        ], dtype=float)
        
        ear = LivenessDetector.eye_aspect_ratio(eye_landmarks)
        assert ear > 0.1  # Open eye should have higher EAR
    
    def test_eye_aspect_ratio_closed_eye(self):
        """Test EAR calculation for closed eye."""
        # Simulated closed eye landmarks (vertical distance near 0)
        eye_landmarks = np.array([
            [0, 0],
            [2, 0.1],
            [2, 0.1],
            [4, 0],
            [2, -0.1],
            [2, -0.1]
        ], dtype=float)
        
        ear = LivenessDetector.eye_aspect_ratio(eye_landmarks)
        assert ear < 0.1  # Closed eye should have lower EAR
    
    def test_liveness_score_initialization(self):
        """Test liveness detector initialization."""
        detector = LivenessDetector(blink_threshold=0.25)
        assert detector.blink_threshold == 0.25
        assert detector.blink_count == 0
        assert detector.previous_ear is None
    
    def test_liveness_detector_reset(self):
        """Test resetting blink counter."""
        detector = LivenessDetector()
        detector.blink_count = 5
        detector.previous_ear = 0.3
        
        detector.reset()
        
        assert detector.blink_count == 0
        assert detector.previous_ear is None
    
    @patch('liveness.mp_face_mesh.FaceMesh')
    def test_compute_liveness_score_no_face(self, mock_face_mesh):
        """Test liveness score when no face detected."""
        mock_instance = MagicMock()
        mock_instance.process.return_value.multi_face_landmarks = None
        mock_face_mesh.return_value.__enter__.return_value = mock_instance
        
        detector = LivenessDetector()
        dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        score = detector.compute_liveness_score(dummy_image)
        assert score == 0.0


class TestEmbeddingDB:
    """Test embedding database operations."""
    
    def test_db_initialization(self):
        """Test database initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/test.db"
            db = EmbeddingDB(db_path)
            
            assert Path(db_path).exists()
    
    def test_store_and_retrieve_embedding(self):
        """Test storing and retrieving an embedding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = EmbeddingDB(f"{tmpdir}/test.db")
            
            embedding = np.random.randn(512)
            emb_id = db.store_embedding(
                application_id="app-001",
                evidence_type="selfie",
                evidence_id="ev-001",
                embedding=embedding,
                file_sha256="abc123",
                file_uri="./test.jpg"
            )
            
            retrieved = db.get_embedding(emb_id)
            
            assert retrieved is not None
            assert np.allclose(retrieved, embedding)
    
    def test_generate_embedding_id(self):
        """Test embedding ID generation is deterministic."""
        id1 = EmbeddingDB._generate_embedding_id("app-001", "ev-001")
        id2 = EmbeddingDB._generate_embedding_id("app-001", "ev-001")
        
        assert id1 == id2
        assert id1.startswith("emb-")
    
    def test_store_verification_result(self):
        """Test storing verification result."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = EmbeddingDB(f"{tmpdir}/test.db")
            
            result_id = db.store_verification_result(
                application_id="app-001",
                embedding_id_selfie="emb-s-001",
                embedding_id_idcrop="emb-i-001",
                similarity=0.89,
                liveness_score=0.95,
                match_confidence=0.91
            )
            
            retrieved = db.get_verification_result(result_id)
            
            assert retrieved is not None
            assert retrieved['application_id'] == "app-001"
            assert retrieved['similarity'] == 0.89
            assert retrieved['liveness_score'] == 0.95
    
    def test_get_embeddings_by_application(self):
        """Test retrieving all embeddings for an application."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = EmbeddingDB(f"{tmpdir}/test.db")
            
            app_id = "app-001"
            emb1 = np.random.randn(512)
            emb2 = np.random.randn(512)
            
            db.store_embedding(app_id, "selfie", "ev-001", emb1)
            db.store_embedding(app_id, "id_crop", "ev-002", emb2)
            
            embeddings = db.get_embeddings_by_application(app_id)
            
            assert "selfie" in embeddings
            assert "id_crop" in embeddings
            assert len(embeddings) == 2


class TestFaceVerificationIntegration:
    """Integration tests for face verification endpoint."""
    
    @pytest.mark.asyncio
    @patch('main.face_utils.process_image_and_get_embedding')
    @patch('main.liveness_detector.compute_liveness_score')
    async def test_verify_face_matching_pair(self, mock_liveness, mock_embedding):
        """Test verification with matching face pair."""
        # Setup: same embedding for both faces (perfect match)
        embedding = np.random.randn(512)
        mock_embedding.side_effect = [
            (embedding, {'detection': {'confidence': 0.95}, 'embedding_dim': 512}),
            (embedding, {'detection': {'confidence': 0.95}, 'embedding_dim': 512})
        ]
        mock_liveness.return_value = 0.95
        
        request = FaceVerificationRequest(
            application_id="app-001",
            id_crop_evidence=EvidenceInput(
                evidence_id="ev-001",
                file_uri="./id_crop.jpg"
            ),
            selfie_evidence=EvidenceInput(
                evidence_id="ev-002",
                file_uri="./selfie.jpg"
            ),
            requested_checks=["similarity", "liveness"]
        )
        
        response = await verify_face(request)
        
        assert response.application_id == "app-001"
        assert response.similarity > 0.95  # Near-perfect match
        assert response.liveness_score == pytest.approx(0.95)
        assert response.match_confidence > 0.90
    
    @pytest.mark.asyncio
    @patch('main.face_utils.process_image_and_get_embedding')
    async def test_verify_face_non_matching_pair(self, mock_embedding):
        """Test verification with non-matching faces."""
        # Setup: different embeddings (no match)
        embedding1 = np.random.randn(512)
        embedding2 = np.random.randn(512)
        
        mock_embedding.side_effect = [
            (embedding1, {'detection': {'confidence': 0.95}, 'embedding_dim': 512}),
            (embedding2, {'detection': {'confidence': 0.95}, 'embedding_dim': 512})
        ]
        
        request = FaceVerificationRequest(
            application_id="app-002",
            id_crop_evidence=EvidenceInput(
                evidence_id="ev-003",
                file_uri="./id_crop.jpg"
            ),
            selfie_evidence=EvidenceInput(
                evidence_id="ev-004",
                file_uri="./selfie.jpg"
            ),
            requested_checks=["similarity"]
        )
        
        response = await verify_face(request)
        
        assert response.application_id == "app-002"
        assert response.similarity < 0.7  # Low similarity for different faces
    
    @pytest.mark.asyncio
    @patch('main.face_utils.process_image_and_get_embedding')
    async def test_verify_face_no_face_detected(self, mock_embedding):
        """Test verification when face detection fails."""
        mock_embedding.return_value = None  # No face detected
        
        request = FaceVerificationRequest(
            application_id="app-003",
            id_crop_evidence=EvidenceInput(
                evidence_id="ev-005",
                file_uri="./invalid.jpg"
            ),
            selfie_evidence=EvidenceInput(
                evidence_id="ev-006",
                file_uri="./selfie.jpg"
            )
        )
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await verify_face(request)
        
        assert exc_info.value.status_code == 400


class TestInputOutputContracts:
    """Test that input/output contracts match specification."""
    
    def test_input_contract_structure(self):
        """Test input request matches contract specification."""
        request = FaceVerificationRequest(
            application_id="app-0001",
            id_crop_evidence=EvidenceInput(
                evidence_id="ev-idcrop-001",
                file_uri="./data/app-0001/ev-idcrop-001.jpg",
                file_sha256="abc123"
            ),
            selfie_evidence=EvidenceInput(
                evidence_id="ev-selfie-001",
                file_uri="./data/app-0001/ev-selfie-001.jpg",
                file_sha256="def456"
            ),
            requested_checks=["similarity", "liveness"]
        )
        
        # Verify all required fields are present
        assert request.application_id == "app-0001"
        assert request.id_crop_evidence.evidence_id == "ev-idcrop-001"
        assert request.selfie_evidence.evidence_id == "ev-selfie-001"
        assert "similarity" in request.requested_checks
        assert "liveness" in request.requested_checks
    
    @pytest.mark.asyncio
    @patch('main.face_utils.process_image_and_get_embedding')
    @patch('main.liveness_detector.compute_liveness_score')
    async def test_output_contract_structure(self, mock_liveness, mock_embedding):
        """Test output response matches contract specification."""
        embedding = np.random.randn(512)
        mock_embedding.side_effect = [
            (embedding, {'detection': {'confidence': 0.95}, 'embedding_dim': 512}),
            (embedding, {'detection': {'confidence': 0.95}, 'embedding_dim': 512})
        ]
        mock_liveness.return_value = 0.95
        
        request = FaceVerificationRequest(
            application_id="app-0001",
            id_crop_evidence=EvidenceInput(
                evidence_id="ev-idcrop-001",
                file_uri="./test.jpg"
            ),
            selfie_evidence=EvidenceInput(
                evidence_id="ev-selfie-001",
                file_uri="./test2.jpg"
            ),
            requested_checks=["similarity", "liveness"]
        )
        
        response = await verify_face(request)
        
        # Verify all required output fields
        assert response.application_id is not None
        assert isinstance(response.similarity, float)
        assert response.similarity_metric == "cosine"
        assert isinstance(response.liveness_score, float)
        assert isinstance(response.match_confidence, float)
        assert response.embedding_id_selfie is not None
        assert response.embedding_id_idcrop is not None
        assert response.agent_version == "face-v1"
        assert response.ts is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
