import cv2
from deepface import DeepFace

class FaceRecognitionHandler:
    def __init__(self, db):
        self.db = db
        self.known_embeddings = []
        self.known_ids = []

    def load_employee_faces(self):
        """Load all employee face embeddings from database"""
        employees = self.db.get_all_employees()
        
        for emp in employees:
            if 'face_embedding' in emp:
                self.known_embeddings.append(emp['face_embedding'])
                self.known_ids.append(emp['militaryID'])

    def verify_face(self, frame):
        """Verify faces in frame against stored embeddings"""
        results = {}
        
        try:
            # Get embedding from current frame
            frame_embedding = DeepFace.represent(
                img_path=frame,
                model_name='Facenet',
                detector_backend="mtcnn",
                enforce_detection=False
            )[0]['embedding']
            
            # Compare against stored embeddings
            for emp_id, known_embedding in zip(self.known_ids, self.known_embeddings):
                distance = DeepFace.dst.findCosineDistance(frame_embedding, known_embedding)
                if distance < 0.4:  # Threshold for verification
                    results[emp_id] = True
        except Exception as e:
            print(f"Error verifying face: {str(e)}")
            
        return results