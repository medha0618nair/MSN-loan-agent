"""
File utilities for handling uploads, checksums, and storage.
"""
import hashlib
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def compute_sha256(file_path: str) -> str:
    """Compute SHA256 hash of file."""
    sha256_hash = hashlib.sha256()
    
    try:
        with open(file_path, "rb") as f:
            # Read in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
        
    except Exception as e:
        logger.error(f"Failed to compute SHA256: {e}")
        return "error_computing_hash"


def ensure_directory(dir_path: str) -> bool:
    """Ensure directory exists."""
    try:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {dir_path}: {e}")
        return False


def save_face_crop(image_array, output_path: str) -> bool:
    """Save face crop image."""
    try:
        from PIL import Image
        
        # Convert array to PIL Image
        img = Image.fromarray(image_array)
        img.save(output_path)
        
        logger.info(f"Face crop saved to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save face crop: {e}")
        return False


def validate_file_exists(file_path: str) -> bool:
    """Validate file exists and is readable."""
    path = Path(file_path)
    
    if not path.exists():
        logger.error(f"File not found: {file_path}")
        return False
    
    if not path.is_file():
        logger.error(f"Path is not a file: {file_path}")
        return False
    
    try:
        with open(file_path, 'rb') as f:
            f.read(1)
        return True
    except Exception as e:
        logger.error(f"File not readable: {e}")
        return False
