from face_recognition_handler import FaceRecognitionHandler
from employee_db import EmployeeDatabase
import cv2
import os

def test_face_loading():
    print("Testing face embedding loading...")
    db = EmployeeDatabase()
    handler = FaceRecognitionHandler(db)
    
    # Load employee faces
    handler.load_employee_faces()
    
    # Verify embeddings were loaded
    print(f"Loaded embeddings: {len(handler.known_embeddings)}")
    print(f"Loaded IDs: {handler.known_ids}")
    
    # Should have embeddings for the 2 employees with valid images
    assert len(handler.known_embeddings) == 2
    assert len(handler.known_ids) == 2
    print("Face loading test passed!")
    return handler, db

def test_face_verification(handler):
    print("\nTesting face verification...")
    # Use an existing employee image as test frame
    test_image_path = "images/employees/177929_alaa.jpg"
    assert os.path.exists(test_image_path)
    
    # Read the image
    frame = cv2.imread(test_image_path)
    
    # Verify against known embeddings
    results = handler.verify_face(frame)
    print(f"Verification results: {results}")
    
    # Should verify successfully against its own embedding
    assert 177929 in results
    assert results[177929] == True
    print("Face verification test passed!")
    return results

if __name__ == "__main__":
    handler, db = test_face_loading()
    verification_results = test_face_verification(handler)
