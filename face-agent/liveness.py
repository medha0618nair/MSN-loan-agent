"""
Liveness detection using blink detection and motion analysis.
"""

import cv2
import numpy as np
try:
    import mediapipe as mp
    MP_FACE_MESH_AVAILABLE = True
except Exception:
    mp = None
    MP_FACE_MESH_AVAILABLE = False
from typing import Optional, Tuple

# Initialize MediaPipe Face Mesh for detailed facial landmarks (if available)
mp_face_mesh = mp.solutions.face_mesh if MP_FACE_MESH_AVAILABLE else None

# Eye landmark indices (from MediaPipe face mesh)
LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]


class LivenessDetector:
    """Detects liveness using blink detection and facial motion analysis."""
    
    def __init__(self, blink_threshold: float = 0.3):
        """
        Initialize liveness detector.
        
        Args:
            blink_threshold: Threshold for eye aspect ratio (EAR) to detect blink
        """
        self.blink_threshold = blink_threshold
        self.blink_count = 0
        self.previous_ear = None
    
    @staticmethod
    def euclidean_distance(point1: np.ndarray, point2: np.ndarray) -> float:
        """
        Calculate Euclidean distance between two points.
        
        Args:
            point1: First point as numpy array
            point2: Second point as numpy array
            
        Returns:
            Euclidean distance
        """
        return np.linalg.norm(point1 - point2)
    
    @staticmethod
    def eye_aspect_ratio(eye_landmarks: np.ndarray) -> float:
        """
        Calculate eye aspect ratio (EAR) for blink detection.
        EAR is based on the ratio of vertical to horizontal eye distances.
        
        Args:
            eye_landmarks: Eye landmarks (6 points)
            
        Returns:
            Eye aspect ratio (0.0 if closed, ~0.3-0.5 if open)
        """
        try:
            if len(eye_landmarks) < 6:
                return 0.0
            
            # Vertical distances
            vertical_1 = LivenessDetector.euclidean_distance(
                eye_landmarks[1], eye_landmarks[5]
            )
            vertical_2 = LivenessDetector.euclidean_distance(
                eye_landmarks[2], eye_landmarks[4]
            )
            
            # Horizontal distance
            horizontal = LivenessDetector.euclidean_distance(
                eye_landmarks[0], eye_landmarks[3]
            )
            
            # Calculate EAR
            ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
            return float(ear)
        
        except Exception as e:
            print(f"Error calculating EAR: {e}")
            return 0.0
    
    def detect_blink(self, image: np.ndarray) -> Tuple[bool, float]:
        """
        Detect eye blink in image.
        
        Args:
            image: Input image as numpy array (RGB format)
            
        Returns:
            Tuple of (blink_detected, eye_aspect_ratio)
        """
        try:
            if MP_FACE_MESH_AVAILABLE and mp_face_mesh is not None:
                with mp_face_mesh.FaceMesh(
                    static_image_mode=False,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                ) as face_mesh:
                    results = face_mesh.process(image)
                    if not results.multi_face_landmarks:
                        return False, 0.0
                    landmarks = results.multi_face_landmarks[0].landmark
                    h, w, _ = image.shape
                    left_eye = np.array([[landmarks[i].x * w, landmarks[i].y * h] for i in LEFT_EYE_INDICES])
                    right_eye = np.array([[landmarks[i].x * w, landmarks[i].y * h] for i in RIGHT_EYE_INDICES])
                    left_ear = self.eye_aspect_ratio(left_eye)
                    right_ear = self.eye_aspect_ratio(right_eye)
                    avg_ear = (left_ear + right_ear) / 2.0
                    blink_detected = False
                    if self.previous_ear is not None:
                        was_open = self.previous_ear > self.blink_threshold
                        is_open = avg_ear > self.blink_threshold
                        if was_open and not is_open:
                            self.blink_count += 1
                            blink_detected = True
                    self.previous_ear = avg_ear
                    return blink_detected, avg_ear

            # Fallback heuristic when MediaPipe is not available
            # Use image-level heuristics: brightness/contrast and variance to approximate liveness
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            # Quick proxy for eye openness using vertical gradients in central face area
            h, w = gray.shape
            cx1 = int(w * 0.25)
            cx2 = int(w * 0.75)
            cy1 = int(h * 0.25)
            cy2 = int(h * 0.75)
            central = gray[cy1:cy2, cx1:cx2]
            # Edge strength as proxy for texture (printed photos low texture)
            edges = cv2.Canny(central, 50, 150)
            edge_score = edges.mean() / 255.0
            # Brightness and contrast
            brightness = np.mean(gray) / 255.0
            contrast = np.std(gray) / 127.0
            brightness_score = 1.0 - abs(brightness - 0.5) * 2
            contrast_score = min(1.0, contrast / 0.5)
            # Combine to a simple proxy EAR and blink detection flag (not real blink)
            proxy_ear = (edge_score + brightness_score + contrast_score) / 3.0
            # If proxy_ear changes significantly from previous, approximate blink
            blink_detected = False
            if self.previous_ear is not None:
                if self.previous_ear > self.blink_threshold and proxy_ear <= self.blink_threshold:
                    self.blink_count += 1
                    blink_detected = True
            self.previous_ear = proxy_ear
            return blink_detected, float(proxy_ear)

        except Exception as e:
            print(f"Error detecting blink: {e}")
            return False, 0.0
    
    def compute_liveness_score(self, image: np.ndarray) -> float:
        """
        Compute liveness score based on multiple factors:
        - Blink detection
        - Facial landmarks presence
        - Image quality
        
        Args:
            image: Input image as numpy array (RGB format)
            
        Returns:
            Liveness score (0.0 to 1.0)
        """
        try:
            if MP_FACE_MESH_AVAILABLE and mp_face_mesh is not None:
                with mp_face_mesh.FaceMesh(
                    static_image_mode=True,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5
                ) as face_mesh:
                    results = face_mesh.process(image)
                    if not results.multi_face_landmarks:
                        return 0.0
                    landmarks = results.multi_face_landmarks[0].landmark
                    valid_landmarks = sum(1 for lm in landmarks if lm.z > 0)
                    landmark_score = min(0.3, (valid_landmarks / len(landmarks)) * 0.3)
                    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                    brightness = np.mean(gray) / 255.0
                    contrast = np.std(gray) / 127.0
                    brightness_score = 1.0 - abs(brightness - 0.5) * 2
                    contrast_score = min(1.0, contrast / 0.5)
                    image_quality_score = (brightness_score + contrast_score) / 2 * 0.3
                    h, w, _ = image.shape
                    face_points = np.array([[landmarks[i].x * w, landmarks[i].y * h] for i in range(len(landmarks)) if landmarks[i].z > 0])
                    if len(face_points) > 10:
                        position_variance = np.var(face_points)
                        variance_score = min(0.4, (position_variance / 10000) * 0.4)
                    else:
                        variance_score = 0.0
                    liveness_score = landmark_score + image_quality_score + variance_score
                    return min(1.0, max(0.0, liveness_score))

            # Fallback heuristic when MediaPipe unavailable
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            brightness = np.mean(gray) / 255.0
            contrast = np.std(gray) / 127.0
            brightness_score = 1.0 - abs(brightness - 0.5) * 2
            contrast_score = min(1.0, contrast / 0.5)
            # Use edge strength in central area as proxy for 3D texture
            h, w, _ = image.shape
            cx1 = int(w * 0.25); cx2 = int(w * 0.75)
            cy1 = int(h * 0.25); cy2 = int(h * 0.75)
            central = gray[cy1:cy2, cx1:cx2]
            edges = cv2.Canny(central, 50, 150)
            edge_score = edges.mean() / 255.0
            # Compose score
            image_quality_score = (brightness_score + contrast_score) / 2.0 * 0.3
            texture_score = min(0.4, edge_score * 0.4)
            liveness_score = image_quality_score + texture_score
            return min(1.0, max(0.0, liveness_score))

        except Exception as e:
            print(f"Error computing liveness score: {e}")
            return 0.0
    
    def reset(self):
        """Reset blink counter and state."""
        self.blink_count = 0
        self.previous_ear = None
