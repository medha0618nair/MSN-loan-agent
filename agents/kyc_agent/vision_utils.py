"""
Vision utilities for face detection and ID card face cropping.
Uses OpenCV and MediaPipe for robust face detection.
"""
import logging
from typing import Optional, Tuple, List
import numpy as np

logger = logging.getLogger(__name__)

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logger.warning("OpenCV not available. Face detection disabled.")

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    logger.warning("MediaPipe not available. Using fallback face detection.")


class FaceDetector:
    """Face detection for ID documents."""
    
    def __init__(self):
        self.use_mediapipe = MEDIAPIPE_AVAILABLE
        
        if self.use_mediapipe:
            self.mp_face_detection = mp.solutions.face_detection
            self.face_detector = self.mp_face_detection.FaceDetection(
                min_detection_confidence=0.5
            )
            logger.info("Initialized MediaPipe face detector")
        elif OPENCV_AVAILABLE:
            # Fallback to Haar Cascade
            try:
                self.face_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                )
                logger.info("Initialized OpenCV Haar Cascade face detector")
            except:
                logger.error("Failed to load Haar Cascade classifier")
                self.face_cascade = None
        else:
            logger.error("No face detection backend available")
    
    def detect_face_mediapipe(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int, float]]:
        """
        Detect face using MediaPipe.
        
        Returns:
            Tuple of (x, y, w, h, confidence) or None
        """
        if not self.use_mediapipe:
            return None
        
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process
            results = self.face_detector.process(rgb_image)
            
            if not results.detections:
                return None
            
            # Get first detection
            detection = results.detections[0]
            
            # Get bounding box
            bbox = detection.location_data.relative_bounding_box
            h, w, _ = image.shape
            
            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            width = int(bbox.width * w)
            height = int(bbox.height * h)
            
            confidence = detection.score[0]
            
            return (x, y, width, height, confidence)
            
        except Exception as e:
            logger.error(f"MediaPipe face detection failed: {e}")
            return None
    
    def detect_face_opencv(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int, float]]:
        """
        Detect face using OpenCV Haar Cascade.
        
        Returns:
            Tuple of (x, y, w, h, confidence) or None
        """
        if not OPENCV_AVAILABLE or not hasattr(self, 'face_cascade') or self.face_cascade is None:
            return None
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            if len(faces) == 0:
                return None
            
            # Get largest face
            largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
            x, y, w, h = largest_face
            
            # Haar Cascade doesn't provide confidence, use fixed value
            confidence = 0.75
            
            return (x, y, w, h, confidence)
            
        except Exception as e:
            logger.error(f"OpenCV face detection failed: {e}")
            return None
    
    def detect_and_crop_face(self, image_path: str) -> Tuple[Optional[np.ndarray], Optional[Tuple], float]:
        """
        Detect face and return cropped image.
        
        Returns:
            Tuple of (cropped_image, bbox, confidence)
        """
        if not OPENCV_AVAILABLE:
            logger.error("OpenCV not available for image loading")
            return None, None, 0.0
        
        try:
            # Load image
            image = cv2.imread(image_path)
            
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return None, None, 0.0
            
            # Try MediaPipe first
            detection = self.detect_face_mediapipe(image)
            
            # Fallback to OpenCV
            if detection is None:
                detection = self.detect_face_opencv(image)
            
            if detection is None:
                logger.warning(f"No face detected in {image_path}")
                return None, None, 0.0
            
            x, y, w, h, confidence = detection
            
            # Add padding
            padding = 20
            x_start = max(0, x - padding)
            y_start = max(0, y - padding)
            x_end = min(image.shape[1], x + w + padding)
            y_end = min(image.shape[0], y + h + padding)
            
            # Crop face
            face_crop = image[y_start:y_end, x_start:x_end]
            
            logger.info(f"Face detected with confidence {confidence:.2f}")
            
            return face_crop, (x, y, w, h), confidence
            
        except Exception as e:
            logger.error(f"Face detection and crop failed: {e}")
            return None, None, 0.0
