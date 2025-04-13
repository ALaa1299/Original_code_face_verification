import pymongo
from datetime import datetime
from pymongo import MongoClient, IndexModel
from pymongo.errors import DuplicateKeyError
from deepface import DeepFace
import numpy as np
from io import BytesIO
from PIL import Image

class EmployeeDatabase:
    def __init__(self, db_name='employee_management', collection_name='employees'):
        try:
            self.client = MongoClient("mongodb+srv://root:example@faceverification.qp2ckht.mongodb.net/?appName=faceverification")
            self.client.server_info()  # Test connection
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.attendance_collection = self.db['attendance']
        self._setup_database()

    def _setup_database(self):
        try:
            if self.collection.name not in self.db.list_collection_names():
                self.db.create_collection(
                    self.collection.name,
                    validator={
                        "$jsonSchema": {
                            "bsonType": "object",
                            "required": ["rank", "fullname", "militaryID", "department", "image_data"],
                            "properties": {
                                "rank": {"bsonType": "string"},
                                "fullname": {"bsonType": "string"},
                                "militaryID": {"bsonType": "int"},
                                "department": {"bsonType": "string"},
                                "image_data": {"bsonType": "binData"},
                                "face_embedding": {"bsonType": "array"}
                            }
                        }
                    }
                )
            index1 = IndexModel([('militaryID', pymongo.ASCENDING)], unique=True)
            self.collection.create_indexes([index1])
        except Exception as e:
            print(f"Warning: {str(e)}")

    def add_employee(self, rank, fullname, militaryID, department, image_data):
        try:
            img = Image.open(BytesIO(image_data))
            embedding = DeepFace.represent(
                img_path=np.array(img),
                model_name='Facenet',
                detector_backend="mtcnn",
                enforce_detection=False
            )[0]['embedding']
            employee_data = {
                'rank': rank,
                'fullname': fullname,
                'militaryID': militaryID,
                'department': department,
                'image_data': image_data,
                'face_embedding': embedding
            }
            self.collection.insert_one(employee_data)
            return f"Successfully added employee {fullname} (ID: {militaryID})"
        except DuplicateKeyError:
            return f"Employee with ID {militaryID} already exists"
        except Exception as e:
            return f"Error adding employee: {str(e)}"

    def get_employee_by_id(self, militaryID):
        return self.collection.find_one({"militaryID": militaryID})

    def record_attendance(self, militaryID, status):
        self.attendance_collection.insert_one({
            "militaryID": militaryID,
            "status": status,
            "timestamp": datetime.now()
        })

    def get_all_employees(self):
        return list(self.collection.find({}))