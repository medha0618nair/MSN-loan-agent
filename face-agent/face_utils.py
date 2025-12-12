"""
Face detection, embedding extraction, and similarity scoring utilities.
Uses MediaPipe for face detection and FaceNet for embeddings.
"""

import cv2
import numpy as np
try:
    import mediapipe as mp
    MP_AVAILABLE = True
except Exception:
    mp = None
    MP_AVAILABLE = False
from pathlib import Path
from typing import Optional, Tuple, List
from PIL import Image
try:
    import onnxruntime as ort
    import urllib.request
    ONNX_AVAILABLE = True
except Exception:
    ONNX_AVAILABLE = False

# Initialize MediaPipe Face Detection if available
if MP_AVAILABLE:
    mp_face_detection = mp.solutions.face_detection
    mp_drawing = mp.solutions.drawing_utils
else:
    mp_face_detection = None
    mp_drawing = None
    # Prepare OpenCV Haar cascade fallback
    try:
        HAAR_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        _haar_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)
    except Exception:
        _haar_cascade = None

# ArcFace ONNX model initialization
_arcface_session = None
_arcface_model_path = "/tmp/arcface.onnx"

def get_arcface_session():
    """Lazily load ArcFace ONNX model."""
    global _arcface_session
    if _arcface_session is None and ONNX_AVAILABLE:
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            # Download model if not present
            if not Path(_arcface_model_path).exists():
                logger.info("Downloading ArcFace ONNX model...")
                model_url = "https://github.com/onnx/models/raw/main/vision/body_analysis/arcface/model/arcfaceresnet100-8.onnx"
                urllib.request.urlretrieve(model_url, _arcface_model_path)
                logger.info("Model downloaded")
            
            logger.info("Loading ArcFace ONNX session...")
            _arcface_session = ort.InferenceSession(_arcface_model_path, providers=['CPUExecutionProvider'])
            logger.info("ArcFace ONNX loaded successfully")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to load ArcFace ONNX: {e}, falling back to lightweight embeddings")
            _arcface_session = None
    return _arcface_session


class FaceUtils:
    """Utilities for face detection and embedding generation."""
    
    @staticmethod
    def load_image(file_uri: str) -> Optional[np.ndarray]:
        """
        Load image from file path.
        
        Args:
            file_uri: Path to image file
            
        Returns:
            Image as numpy array or None if failed
        """
        try:
            path = Path(file_uri)
            if not path.exists():
                raise FileNotFoundError(f"Image not found: {file_uri}")
            
            image = cv2.imread(str(path))
            if image is None:
                raise ValueError(f"Failed to load image: {file_uri}")
            
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return image
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
    
    @staticmethod
    def detect_face(image: np.ndarray) -> Optional[Tuple[np.ndarray, dict]]:
        """
        Detect face in image using MediaPipe.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Tuple of (cropped face, detection metadata) or None if no face found
        """
        try:
            # Prefer MediaPipe if available
            if MP_AVAILABLE and mp_face_detection is not None:
                with mp_face_detection.FaceDetection(
                    model_selection=1,
                    min_detection_confidence=0.5
                ) as face_detection:
                    results = face_detection.process(image)
                    if not results.detections:
                        return None
                    detection = results.detections[0]
                    bbox = detection.location_data.relative_bounding_box
                    h, w, _ = image.shape
                    x1 = int(bbox.xmin * w)
                    y1 = int(bbox.ymin * h)
                    x2 = int((bbox.xmin + bbox.width) * w)
                    y2 = int((bbox.ymin + bbox.height) * h)
                    x1 = max(0, x1)
                    y1 = max(0, y1)
                    x2 = min(w, x2)
                    y2 = min(h, y2)
                    margin = int(0.1 * (x2 - x1))
                    x1 = max(0, x1 - margin)
                    y1 = max(0, y1 - margin)
                    x2 = min(w, x2 + margin)
                    y2 = min(h, y2 + margin)
                    face_crop = image[y1:y2, x1:x2]
                    metadata = {
                        'bbox': (x1, y1, x2, y2),
                        'confidence': float(detection.score[0]) if detection.score else None,
                        'keypoints': getattr(detection.location_data, 'relative_keypoints', None)
                    }
                    return face_crop, metadata

            # Fallback: OpenCV Haar Cascade
            if _haar_cascade is not None:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                faces = _haar_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
                if len(faces) == 0:
                    return None
                # Use first detected face
                x, y, w_box, h_box = faces[0]
                x1 = max(0, x)
                y1 = max(0, y)
                x2 = x1 + w_box
                y2 = y1 + h_box
                margin = int(0.1 * (x2 - x1))
                x1 = max(0, x1 - margin)
                y1 = max(0, y1 - margin)
                x2 = min(image.shape[1], x2 + margin)
                y2 = min(image.shape[0], y2 + margin)
                face_crop = image[y1:y2, x1:x2]
                metadata = {
                    'bbox': (x1, y1, x2, y2),
                    'confidence': None,
                    'keypoints': None
                }
                return face_crop, metadata

            return None

        except Exception as e:
            print(f"Error detecting face: {e}")
            return None
    
    @staticmethod
    def get_embedding(face_crop: np.ndarray) -> Optional[np.ndarray]:
        """
        Generate face embedding using ArcFace ONNX or lightweight fallback.
        
        Args:
            face_crop: Cropped face image as numpy array (RGB)
            
        Returns:
            Face embedding (512-dim ArcFace or 256-dim fallback) or None if failed
        """
        try:
            # Try ArcFace ONNX first
            session = get_arcface_session()
            if session is not None:
                # Preprocess for ArcFace (112x112, normalized)
                face_resized = cv2.resize(face_crop, (112, 112))
                face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_RGB2BGR)
                
                # Normalize (ImageNet style)
                face_norm = face_rgb.astype(np.float32)
                face_norm = (face_norm - np.array([104.0, 117.0, 123.0])) / 255.0
                face_norm = np.transpose(face_norm, (2, 0, 1))
                face_norm = np.expand_dims(face_norm, 0)
                
                # Inference
                input_name = session.get_inputs()[0].name
                output_name = session.get_outputs()[0].name
                embedding = session.run([output_name], {input_name: face_norm})[0]
                embedding = embedding.flatten().astype(np.float32)
                
                # Normalize to unit vector for cosine similarity
                embedding = embedding / (np.linalg.norm(embedding) + 1e-6)
                return embedding
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"ArcFace inference failed: {e}, using lightweight fallback")
        
        # Fallback: lightweight feature extraction
        try:
            face_resized = cv2.resize(face_crop, (160, 160))
            face_gray = cv2.cvtColor(face_resized, cv2.COLOR_RGB2GRAY)
            
            # Simple texture + color features
            sobelx = cv2.Sobel(face_gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(face_gray, cv2.CV_64F, 0, 1, ksize=3)
            magnitude = np.sqrt(sobelx**2 + sobely**2)
            angle = np.arctan2(sobely, sobelx) * 180 / np.pi
            
            hog_feature = np.zeros(9)
            for i in range(magnitude.shape[0]):
                for j in range(magnitude.shape[1]):
                    bin_idx = int((angle[i, j] + 180) / 40) % 9
                    hog_feature[bin_idx] += magnitude[i, j]
            hog_feature = hog_feature / (np.sum(hog_feature) + 1e-6)
            
            color_hist = np.zeros(48)
            for channel_idx, channel in enumerate([0, 1, 2]):
                hist = cv2.calcHist([face_resized], [channel], None, [16], [0, 256])
                color_hist[channel_idx*16:(channel_idx+1)*16] = hist.flatten() / (np.sum(hist) + 1e-6)
            
            edges = cv2.Canny(face_gray, 50, 150)
            edge_feature = np.array([
                np.sum(edges) / edges.size,
                np.std(face_gray),
                np.mean(face_gray)
            ])
            
            embedding = np.concatenate([
                hog_feature,
                color_hist,
                edge_feature,
                np.zeros(256 - len(hog_feature) - len(color_hist) - len(edge_feature))
            ])
            
            return embedding[:256].astype(np.float32)
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error generating embedding: {e}")
            return None
    
    @staticmethod
    def compute_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        try:
            # Normalize embeddings
            emb1_norm = embedding1 / np.linalg.norm(embedding1)
            emb2_norm = embedding2 / np.linalg.norm(embedding2)
            
            # Compute cosine similarity
            similarity = np.dot(emb1_norm, emb2_norm)
            
            # Ensure in [0, 1] range
            similarity = max(0.0, min(1.0, (similarity + 1) / 2))
            
            return float(similarity)
        
        except Exception as e:
            print(f"Error computing similarity: {e}")
            return 0.0
    
    @staticmethod
    def process_image_and_get_embedding(
        file_uri: str
    ) -> Optional[Tuple[np.ndarray, dict]]:
        """
        Complete pipeline: load image -> detect face -> get embedding.
        
        Args:
            file_uri: Path to image file
            
        Returns:
            Tuple of (embedding, metadata) or None if failed
        """
        try:
            # Load image
            image = FaceUtils.load_image(file_uri)
            if image is None:
                return None
            
            # Detect face
            result = FaceUtils.detect_face(image)
            if result is None:
                return None
            
            face_crop, detection_metadata = result
            
            # Get embedding
            embedding = FaceUtils.get_embedding(face_crop)
            if embedding is None:
                return None
            
            metadata = {
                'detection': detection_metadata,
                'embedding_dim': len(embedding)
            }
            
            return embedding, metadata
        
        except Exception as e:
            print(f"Error in full processing pipeline: {e}")
            return None
    
    @staticmethod
    def process_image_and_get_embedding_from_array(image_array: np.ndarray) -> Optional[np.ndarray]:
        """
        Complete pipeline on numpy array: detect face -> get embedding.
        
        Args:
            image_array: Image as numpy array (RGB format)
            
        Returns:
            Embedding as numpy array or None if failed
        """
        try:
            # Detect face
            result = FaceUtils.detect_face(image_array)
            if result is None:
                return None
            
            face_crop, _ = result
            
            # Get embedding
            embedding = FaceUtils.get_embedding(face_crop)
            return embedding
        
        except Exception as e:
            print(f"Error processing image array: {e}")
            return None
