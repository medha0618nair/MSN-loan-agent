"""
FastAPI microservice for face and liveness verification.
Exported as a LangChain Tool for use in multi-agent orchestration.
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import logging
from langchain.tools import tool
import os
import io
from PIL import Image
import numpy as np

from face_utils import FaceUtils
from liveness import LivenessDetector
from db import EmbeddingDB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
app = FastAPI(
    title="Face & Liveness Verification Agent",
    description="Verifies face identity and liveness for loan origination",
    version="1.0.0"
)

# Initialize database
db = EmbeddingDB("embeddings.db")

# Initialize face utilities and liveness detector
face_utils = FaceUtils()
liveness_detector = LivenessDetector()

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class EvidenceInput(BaseModel):
    """Single piece of evidence (image)."""
    evidence_id: str
    file_uri: str
    file_sha256: Optional[str] = None


class FaceVerificationRequest(BaseModel):
    """Input request for face verification."""
    application_id: str
    id_crop_evidence: EvidenceInput
    selfie_evidence: EvidenceInput
    requested_checks: List[str] = ["similarity", "liveness"]


class FaceVerificationResponse(BaseModel):
    """Output response from face verification."""
    application_id: str
    similarity: float
    similarity_metric: str
    liveness_score: float
    match_confidence: float
    embedding_id_selfie: str
    embedding_id_idcrop: str
    agent_version: str
    ts: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="face-v1",
        timestamp=datetime.utcnow().isoformat()
    )


@app.post("/face/verify", response_model=FaceVerificationResponse)
async def verify_face(
    id_crop: UploadFile = File(...),
    selfie: UploadFile = File(...),
    application_id: str = Form(...),
    subject_id: str = Form(...)
) -> FaceVerificationResponse:
    """
    Verify face identity and liveness.
    
    Input contract:
    {
        "application_id": "app-0001",
        "id_crop_evidence": {
            "evidence_id": "ev-idcrop-001",
            "file_uri": "./data/app-0001/ev-idcrop-001.jpg",
            "file_sha256": "..."
        },
        "selfie_evidence": {
            "evidence_id": "ev-selfie-001",
            "file_uri": "./data/app-0001/ev-selfie-001.jpg",
            "file_sha256": "..."
        },
        "requested_checks": ["similarity", "liveness"]
    }
    
    Output contract:
    {
        "application_id": "app-0001",
        "similarity": 0.89,
        "similarity_metric": "cosine",
        "liveness_score": 0.95,
        "match_confidence": 0.87,
        "embedding_id_selfie": "emb-s-001",
        "embedding_id_idcrop": "emb-i-001",
        "agent_version": "face-v1",
        "ts": "2024-01-15T10:30:45.123456"
    }
    """
    try:
        logger.info(f"Processing face verification for {request.application_id}")
        
        # ===================================================================
        # STEP 1: Process ID Crop Image
        # ===================================================================
        logger.info(f"Processing ID crop: {request.id_crop_evidence.file_uri}")
        
        id_crop_result = face_utils.process_image_and_get_embedding(
            request.id_crop_evidence.file_uri
        )
        
        if id_crop_result is None:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to detect face in ID crop: {request.id_crop_evidence.file_uri}"
            )
        
        id_crop_embedding, id_crop_metadata = id_crop_result
        
        # Store ID crop embedding
        embedding_id_idcrop = db.store_embedding(
            application_id=request.application_id,
            evidence_type="id_crop",
            evidence_id=request.id_crop_evidence.evidence_id,
            embedding=id_crop_embedding,
            file_sha256=request.id_crop_evidence.file_sha256,
            file_uri=request.id_crop_evidence.file_uri,
            detection_confidence=id_crop_metadata['detection']['confidence']
        )
        logger.info(f"Stored ID crop embedding: {embedding_id_idcrop}")
        
        # ===================================================================
        # STEP 2: Process Selfie Image
        # ===================================================================
        logger.info(f"Processing selfie: {request.selfie_evidence.file_uri}")
        
        selfie_result = face_utils.process_image_and_get_embedding(
            request.selfie_evidence.file_uri
        )
        
        if selfie_result is None:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to detect face in selfie: {request.selfie_evidence.file_uri}"
            )
        
        selfie_embedding, selfie_metadata = selfie_result
        
        # Store selfie embedding
        embedding_id_selfie = db.store_embedding(
            application_id=request.application_id,
            evidence_type="selfie",
            evidence_id=request.selfie_evidence.evidence_id,
            embedding=selfie_embedding,
            file_sha256=request.selfie_evidence.file_sha256,
            file_uri=request.selfie_evidence.file_uri,
            detection_confidence=selfie_metadata['detection']['confidence']
        )
        logger.info(f"Stored selfie embedding: {embedding_id_selfie}")
        
        # ===================================================================
        # STEP 3: Compute Similarity (if requested)
        # ===================================================================
        similarity_score = 0.0
        similarity_metric = "cosine"
        
        if "similarity" in request.requested_checks:
            similarity_score = face_utils.compute_similarity(
                id_crop_embedding,
                selfie_embedding
            )
            logger.info(f"Similarity score: {similarity_score}")
        
        # ===================================================================
        # STEP 4: Compute Liveness (if requested)
        # ===================================================================
        liveness_score = 0.0
        
        if "liveness" in request.requested_checks:
            # Load selfie image for liveness detection
            selfie_image = face_utils.load_image(request.selfie_evidence.file_uri)
            
            if selfie_image is not None:
                liveness_score = liveness_detector.compute_liveness_score(selfie_image)
                logger.info(f"Liveness score: {liveness_score}")
            else:
                logger.warning("Failed to load selfie for liveness check")
                liveness_score = 0.0
        
        # ===================================================================
        # STEP 5: Compute Match Confidence (Weighted Average)
        # ===================================================================
        # match_confidence = 0.7 * similarity + 0.3 * liveness
        weights_similarity = 0.7
        weights_liveness = 0.3
        match_confidence = (
            weights_similarity * similarity_score +
            weights_liveness * liveness_score
        )
        logger.info(f"Match confidence: {match_confidence}")
        
        # ===================================================================
        # STEP 6: Store Verification Result
        # ===================================================================
        db.store_verification_result(
            application_id=request.application_id,
            embedding_id_selfie=embedding_id_selfie,
            embedding_id_idcrop=embedding_id_idcrop,
            similarity=similarity_score,
            similarity_metric=similarity_metric,
            liveness_score=liveness_score,
            match_confidence=match_confidence,
            agent_version="face-v1"
        )
        
        # ===================================================================
        # STEP 7: Return Response
        # ===================================================================
        response = FaceVerificationResponse(
            application_id=request.application_id,
            similarity=round(similarity_score, 4),
            similarity_metric=similarity_metric,
            liveness_score=round(liveness_score, 4),
            match_confidence=round(match_confidence, 4),
            embedding_id_selfie=embedding_id_selfie,
            embedding_id_idcrop=embedding_id_idcrop,
            agent_version="face-v1",
            ts=datetime.utcnow().isoformat()
        )
        
        logger.info(f"Face verification completed for {request.application_id}")
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# ============================================================================
# LANGCHAIN TOOL WRAPPER
# ============================================================================

@tool("face_verify")
def face_verify(
    application_id: str,
    id_crop_file_uri: str,
    selfie_file_uri: str,
    id_crop_evidence_id: str = None,
    selfie_evidence_id: str = None,
    id_crop_sha256: str = None,
    selfie_sha256: str = None,
    requested_checks: List[str] = None
) -> dict:
    """
    LangChain Tool for face and liveness verification.
    
    Used by the orchestrator agent to verify face identity and liveness.
    
    Args:
        application_id: Unique application identifier
        id_crop_file_uri: Path to ID document face crop image
        selfie_file_uri: Path to user selfie image
        id_crop_evidence_id: Evidence ID for ID crop (auto-generated if not provided)
        selfie_evidence_id: Evidence ID for selfie (auto-generated if not provided)
        id_crop_sha256: SHA256 hash of ID crop image
        selfie_sha256: SHA256 hash of selfie image
        requested_checks: List of checks to perform (default: ["similarity", "liveness"])
    
    Returns:
        dict: Verification result with similarity, liveness, and match confidence scores
    
    Example:
        >>> face_verify(
        ...     application_id="app-0001",
        ...     id_crop_file_uri="./data/app-0001/id_crop.jpg",
        ...     selfie_file_uri="./data/app-0001/selfie.jpg"
        ... )
        {
            'application_id': 'app-0001',
            'similarity': 0.89,
            'similarity_metric': 'cosine',
            'liveness_score': 0.95,
            'match_confidence': 0.87,
            'embedding_id_selfie': 'emb-s-001',
            'embedding_id_idcrop': 'emb-i-001',
            'agent_version': 'face-v1',
            'ts': '2024-01-15T10:30:45.123456'
        }
    """
    try:
        # Auto-generate evidence IDs if not provided
        id_crop_evidence_id = id_crop_evidence_id or f"ev-idcrop-{application_id}"
        selfie_evidence_id = selfie_evidence_id or f"ev-selfie-{application_id}"
        requested_checks = requested_checks or ["similarity", "liveness"]
        
        # Create request
        request = FaceVerificationRequest(
            application_id=application_id,
            id_crop_evidence=EvidenceInput(
                evidence_id=id_crop_evidence_id,
                file_uri=id_crop_file_uri,
                file_sha256=id_crop_sha256
            ),
            selfie_evidence=EvidenceInput(
                evidence_id=selfie_evidence_id,
                file_uri=selfie_file_uri,
                file_sha256=selfie_sha256
            ),
            requested_checks=requested_checks
        )
        
        # Process synchronously (simulate sync call within tool)
        import asyncio
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(verify_face(request))
        loop.close()
        
        # Return as dictionary
        return response.dict()
    
    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        return {
            "error": str(e),
            "application_id": application_id,
            "agent_version": "face-v1",
            "ts": datetime.utcnow().isoformat()
        }


# ============================================================================
# APPLICATION STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Face Verification Agent starting...")
    logger.info("Database initialized")
    logger.info("Face detection and embedding models loaded")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Face Verification Agent shutting down...")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
