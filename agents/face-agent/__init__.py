"""Face Verification Agent Package."""

__version__ = "1.0.0"
__author__ = "MSN UNISYS"
__description__ = "Face & Liveness Verification Agent for Loan Origination"

from face_utils import FaceUtils
from liveness import LivenessDetector
from db import EmbeddingDB

__all__ = [
    "FaceUtils",
    "LivenessDetector",
    "EmbeddingDB"
]
