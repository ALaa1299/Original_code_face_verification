import cv2
from deepface import DeepFace
import tempfile
import os
import numpy as np
from functools import lru_cache

class FaceRecognitionHandler:
    def __init__(self, db):
        self.db = db
        self.known_embeddings = []
        self.known_ids = []
        self.employee_cache = {}

    @lru_cache(maxsize=32)
    def _get_embedding(self, image_path):
        """Cached face embedding extraction"""
        try:
            result = DeepFace.represent(
                img_path=image_path,
                model_name='Facenet',
                detector_backend="mtcnn",
                enforce_detection=False
            )
            return result[0]['embedding'] if result else None
        except Exception as e:
            print(f"Embedding extraction failed for {image_path}: {str(e)}")
            return None

    def load_employee_faces(self):
        """Load all employee face embeddings for verification."""
        employees = self.db.get_all_employees()
        
        for emp in employees:
            if emp.get('image_path'):
                try:
                    if os.path.exists(emp['image_path']):
                        embedding = DeepFace.represent(
                            img_path=emp['image_path'],
                            model_name='Facenet',
                            detector_backend="mtcnn",
                            enforce_detection=False
                        )
                        if embedding:
                            self.known_embeddings.append(embedding[0]['embedding'])
                            self.known_ids.append(emp['militaryID'])
                except Exception as e:
                    print(f"Failed to process image for ID {emp['militaryID']}: {str(e)}")

    def verify_face(self, frame):
        """Verify faces in the provided frame against known embeddings."""
        results = {}
        
        # Save frame to temp file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            cv2.imwrite(tmp.name, frame)
            frame_path = tmp.name
            
        try:
            # Compare frame against each employee image
            for emp_id, emp in zip(self.known_ids, self.db.get_all_employees()):
                if not emp.get('image_path'):
                    continue
                    
                try:
                    result = DeepFace.verify(
                        img1_path=frame_path,
                        img2_path=emp['image_path'],
                        model_name='Facenet',
                        detector_backend="mtcnn",
                        distance_metric='cosine',
                        enforce_detection=False
                    )
                    
                    if result['verified'] and result['distance'] < 0.4:
                        results[emp_id] = True
                except Exception as e:
                    print(f"Error verifying face for {emp_id}: {str(e)}")
                    
        finally:
            os.unlink(frame_path)
            
        return results