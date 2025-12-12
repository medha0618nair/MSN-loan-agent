"""
FastAPI microservice for face and liveness verification.
Accepts multipart file uploads and returns verification results.
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import json
import logging
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
# RESPONSE MODELS
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str


class FaceVerificationResponse(BaseModel):
    """Output response from face verification."""
    match_confidence: float
    similarity: float
    liveness: float
    match: bool
    id_embedding_id: str
    selfie_embedding_id: str
    details: dict


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
    id_crop: UploadFile = File(..., description="ID face crop image file"),
    selfie: UploadFile = File(..., description="Live selfie image file"),
    application_id: str = Form(..., description="Application identifier"),
    subject_id: str = Form(..., description="Subject/user identifier")
) -> FaceVerificationResponse:
    """
    Verify face identity and liveness from multipart form-data (file uploads).
    
    **Form Fields:**
    - `id_crop`: ID face crop image file (JPG/PNG) - required
    - `selfie`: Live selfie image file (JPG/PNG) - required
    - `application_id`: Application identifier - required
    - `subject_id`: Subject/user identifier - required
    
    **Response:**
    ```json
    {
        "match_confidence": 0.82,
        "similarity": 0.87,
        "liveness": 0.65,
        "match": true,
        "id_embedding_id": "emb-xxxx",
        "selfie_embedding_id": "emb-yyyy",
        "details": {
            "threshold": 0.8,
            "similarity_normalized": 0.87
        }
    }
    ```
    """
    try:
        logger.info(f"Processing face verification for {application_id}/{subject_id}")
        
        # ===================================================================
        # Step 1: Read and parse image files
        # ===================================================================
        logger.info(f"Reading ID crop image: {id_crop.filename}")
        id_crop_bytes = await id_crop.read()
        
        logger.info(f"Reading selfie image: {selfie.filename}")
        selfie_bytes = await selfie.read()
        
        # Convert bytes to numpy arrays using PIL
        try:
            id_crop_img = Image.open(io.BytesIO(id_crop_bytes)).convert("RGB")
            selfie_img = Image.open(io.BytesIO(selfie_bytes)).convert("RGB")
            
            id_crop_array = np.array(id_crop_img)
            selfie_array = np.array(selfie_img)
            logger.info(f"Images loaded: ID crop shape {id_crop_array.shape}, Selfie shape {selfie_array.shape}")
            
            # Resize large images to prevent memory issues
            MAX_DIM = 512
            if id_crop_array.shape[0] > MAX_DIM or id_crop_array.shape[1] > MAX_DIM:
                logger.info(f"Resizing ID crop from {id_crop_array.shape} to max {MAX_DIM}px...")
                pil_img = Image.fromarray(id_crop_array)
                pil_img.thumbnail((MAX_DIM, MAX_DIM), Image.Resampling.LANCZOS)
                id_crop_array = np.array(pil_img)
                logger.info(f"ID crop resized to {id_crop_array.shape}")
            
            if selfie_array.shape[0] > MAX_DIM or selfie_array.shape[1] > MAX_DIM:
                logger.info(f"Resizing selfie from {selfie_array.shape} to max {MAX_DIM}px...")
                pil_img = Image.fromarray(selfie_array)
                pil_img.thumbnail((MAX_DIM, MAX_DIM), Image.Resampling.LANCZOS)
                selfie_array = np.array(pil_img)
                logger.info(f"Selfie resized to {selfie_array.shape}")
        except Exception as e:
            logger.error(f"Failed to decode images: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")
        
        # ===================================================================
        # Step 2: Extract embeddings from both images
        # ===================================================================
        logger.info("Extracting embedding from ID crop...")
        try:
            id_crop_embedding = face_utils.process_image_and_get_embedding_from_array(id_crop_array)
        except Exception as e:
            logger.error(f"Error extracting ID crop embedding: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Face embedding extraction failed: {str(e)}")
        
        if id_crop_embedding is None:
            logger.error("Could not detect face in ID crop image")
            raise HTTPException(status_code=400, detail="Could not detect face in ID crop image")
        
        logger.info("Extracting embedding from selfie...")
        try:
            selfie_embedding = face_utils.process_image_and_get_embedding_from_array(selfie_array)
        except Exception as e:
            logger.error(f"Error extracting selfie embedding: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Face embedding extraction failed: {str(e)}")
        
        if selfie_embedding is None:
            logger.error("Could not detect face in selfie image")
            raise HTTPException(status_code=400, detail="Could not detect face in selfie image")
        
        logger.info(f"Embeddings extracted: ID crop {id_crop_embedding.shape}, Selfie {selfie_embedding.shape}")
        
        # ===================================================================
        # Step 3: Compute similarity
        # ===================================================================
        logger.info("Computing similarity...")
        similarity = face_utils.compute_similarity(id_crop_embedding, selfie_embedding)
        logger.info(f"Similarity score: {similarity:.4f}")
        
        # ===================================================================
        # Step 4: (optional) Detect liveness on selfie — kept for diagnostics
        # ===================================================================
        logger.info("Computing liveness score (diagnostic)...")
        liveness_score = liveness_detector.compute_liveness_score(selfie_array)
        logger.info(f"Liveness score: {liveness_score:.4f}")

        # ===================================================================
        # Step 5: Compute match confidence (use similarity only)
        # ===================================================================
        # match_confidence now equals pure similarity (ignore liveness by policy)
        match_confidence = float(similarity)
        logger.info(f"Match confidence (similarity-only): {match_confidence:.4f}")
        
        # ===================================================================
        # Step 6: Store embeddings
        # ===================================================================
        logger.info("Storing embeddings in database...")
        id_crop_emb_id = db.store_embedding(
            application_id, 
            "id_crop", 
            subject_id, 
            id_crop_embedding
        )
        selfie_emb_id = db.store_embedding(
            application_id, 
            "selfie", 
            subject_id, 
            selfie_embedding
        )
        logger.info(f"Stored embeddings: ID crop {id_crop_emb_id}, Selfie {selfie_emb_id}")
        
        # ===================================================================
        # Step 7: Determine match result
        # ===================================================================
        threshold = 0.5  # ArcFace cosine similarity threshold (0.5 is standard for face matching)
        # policy: decide match based solely on similarity
        match = similarity >= threshold
        logger.info(f"Match result (similarity-only): {match} (similarity >= {threshold})")
        
        # ===================================================================
        # Step 8: Store verification result
        # ===================================================================
        db.store_verification_result(
            application_id,
            selfie_emb_id,
            id_crop_emb_id,
            float(similarity),
            liveness_score=float(liveness_score),
            match_confidence=float(match_confidence)
        )
        
        # ===================================================================
        # Step 9: Return response
        # ===================================================================
        response = FaceVerificationResponse(
            match_confidence=float(match_confidence),
            similarity=float(similarity),
            liveness=float(liveness_score),
            match=match,
            id_embedding_id=id_crop_emb_id,
            selfie_embedding_id=selfie_emb_id,
            details={
                "threshold": threshold,
                "similarity_normalized": float(similarity),
                "liveness_normalized": float(liveness_score)
            }
        )
        
        logger.info(f"Face verification completed successfully for {application_id}/{subject_id}")
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in verify_face: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


# ============================================================================
# APPLICATION LIFECYCLE
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
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
