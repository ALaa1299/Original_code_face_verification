import cv2
from deepface import DeepFace
import numpy as np
import logging
from deepface.commons import distance as dst

class FaceRecognitionHandler:
    def __init__(self, db):
        self.db = db
        self.known_embeddings = []
        self.known_ids = []
        self.logger = logging.getLogger(__name__)
        self.threshold = 0.4  # Adjustable verification threshold

    def load_employee_faces(self):
        """Load all employee face embeddings from database"""
        try:
            employees = self.db.get_all_employees()
            for emp in employees:
                if 'face_embedding' in emp:
                    self.known_embeddings.append(np.array(emp['face_embedding']))
                    self.known_ids.append(emp['militaryID'])
            self.logger.info(f"Loaded {len(self.known_ids)} employee face embeddings")
        except Exception as e:
            self.logger.error(f"Error loading employee faces: {str(e)}")

    def verify_face(self, frame):
        """Verify a face against known embeddings"""
        results = {}
        try:
            # Get embedding from current frame
            frame_embedding = DeepFace.represent(
                img_path=frame,
                model_name='Facenet',
                detector_backend="mtcnn",
                enforce_detection=False
            )[0]['embedding']
            frame_embedding = np.array(frame_embedding)

            # Compare against all known embeddings
            for emp_id, known_embedding in zip(self.known_ids, self.known_embeddings):
                try:
                    distance = dst.findCosineDistance(frame_embedding, known_embedding)
                    results[emp_id] = distance < self.threshold
                except Exception as e:
                    self.logger.warning(f"Error comparing with ID {emp_id}: {str(e)}")
                    results[emp_id] = False

        except Exception as e:
            self.logger.error(f"Face verification error: {str(e)}")
        
        return results

    def set_verification_threshold(self, threshold):
        """Adjust the verification threshold (0-1)"""
        self.threshold = threshold
