import pymongo
from datetime import datetime
from pymongo import MongoClient, IndexModel
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from deepface import DeepFace
import numpy as np
from io import BytesIO
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmployeeDatabase:
    _instance = None

    @classmethod
    def get_instance(cls, db_name='employee_management', collection_name='employees'):
        if cls._instance is None:
            cls._instance = cls(db_name, collection_name)
        return cls._instance

    def __init__(self, db_name='employee_management', collection_name='employees'):
        self.client = None
        self.db = None
        self.collection = None
        self.attendance_collection = None
        self._connect_to_mongodb(db_name, collection_name)

    def _connect_to_mongodb(self, db_name, collection_name):
        try:
            self.client = MongoClient(
                "mongodb+srv://root:example@faceverification.qp2ckht.mongodb.net/?retryWrites=true&w=majority",
                serverSelectionTimeoutMS=5000
            )
            self.client.server_info()  # Test connection
            
            if db_name in self.client.list_database_names():
                self.db = self.client[db_name]
                self.collection = self.db[collection_name]
                self.attendance_collection = self.db['attendance']
                logger.info("Connected to existing database")
            else:
                self.db = self.client[db_name]
                self.collection = self.db[collection_name]
                self.attendance_collection = self.db['attendance']
                self._setup_database()
                logger.info("Successfully created new database and collection")
            
            logger.info("Successfully connected to MongoDB")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    def _setup_database(self):
        try:
            # First try to update existing collection schema
            if self.collection.name in self.db.list_collection_names():
                try:
                    self.db.command({
                        'collMod': self.collection.name,
                        'validator': {
                            "$jsonSchema": {
                                "bsonType": "object",
                                "required": ["rank", "fullname", "militaryID", "department", "image_binary", "face_embedding"],
                                "properties": {
                                    "rank": {"bsonType": "string"},
                                    "fullname": {"bsonType": "string"},
                                    "militaryID": {"bsonType": "int"},
                                    "department": {"bsonType": "string"},
                                    "image_binary": {"bsonType": "binData"},
                                    "face_embedding": {"bsonType": "array"},
                                    "created_at": {"bsonType": "date"}
                                }
                            }
                        }
                    })
                    logger.info("Successfully updated collection validator")
                except Exception as e:
                    logger.warning(f"Could not update collection validator: {str(e)}")
                    logger.warning("Dropping and recreating collection...")
                    self.collection.drop()
            
            # Create collection with new schema
            self.db.create_collection(
                self.collection.name,
                validator={
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["rank", "fullname", "militaryID", "department", "image_binary", "face_embedding"],
                        "properties": {
                            "rank": {"bsonType": "string"},
                            "fullname": {"bsonType": "string"},
                            "militaryID": {"bsonType": "int"},
                            "department": {"bsonType": "string"},
                            "image_binary": {"bsonType": "binData"},
                            "face_embedding": {"bsonType": "array"},
                            "created_at": {"bsonType": "date"}
                        }
                    }
                }
            )
            
            # Create indexes
            index1 = IndexModel([('militaryID', pymongo.ASCENDING)], unique=True)
            self.collection.create_indexes([index1])
            
        except Exception as e:
            logger.warning(f"Database setup warning: {str(e)}")

    def add_employee(self, rank, fullname, militaryID, department, image_data):
        try:
            img = Image.open(BytesIO(image_data))
            embedding = DeepFace.represent(
                img_path=np.array(img),
                model_name='Facenet',
                detector_backend="mtcnn",
                enforce_detection=True
            )[0]['embedding']
            
            employee_data = {
                'rank': rank,
                'fullname': fullname,
                'militaryID': militaryID,
                'department': department,
                'image_binary': image_data,
                'face_embedding': embedding,
                'created_at': datetime.now()
            }
            
            self.collection.insert_one(employee_data)
            return f"Successfully added employee {fullname} (ID: {militaryID})"
        except DuplicateKeyError:
            return f"Employee with ID {militaryID} already exists"
        except Exception as e:
            logger.error(f"Error adding employee: {str(e)}")
            return f"Error adding employee: {str(e)}"

    def get_employee_by_id(self, militaryID):
        try:
            return self.collection.find_one({"militaryID": militaryID})
        except Exception as e:
            logger.error(f"Error fetching employee: {str(e)}")
            return None

    def record_attendance(self, militaryID, status):
        try:
            self.attendance_collection.insert_one({
                "militaryID": militaryID,
                "status": status,
                "timestamp": datetime.now()
            })
        except Exception as e:
            logger.error(f"Error recording attendance: {str(e)}")

    def get_all_employees(self):
        try:
            return list(self.collection.find({}))
        except Exception as e:
            logger.error(f"Error fetching employees: {str(e)}")
            return []

    def get_attendance_by_employee(self, militaryID):
        """Get all attendance records for a specific employee"""
        try:
            return list(self.attendance_collection.find(
                {"militaryID": militaryID},
                {"_id": 0}
            ).sort("timestamp", pymongo.DESCENDING))
        except Exception as e:
            logger.error(f"Error fetching attendance records: {str(e)}")
            return []

    def delete_employee_attendance(self, militaryID):
        """Delete all attendance records for a specific employee"""
        try:
            result = self.attendance_collection.delete_many({"militaryID": militaryID})
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting attendance records: {str(e)}")
            return 0
