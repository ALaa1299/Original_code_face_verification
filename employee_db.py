import os
import pymongo
from datetime import datetime
from pymongo import MongoClient, IndexModel
from pymongo.errors import DuplicateKeyError, OperationFailure

class EmployeeDatabase:
    def __init__(self, db_name='employee_management', collection_name='employees'):
        """Initialize MongoDB connection and setup database"""
        # Get credentials from environment variables
        mongo_user = os.getenv("MONGO_USER", "root")
        mongo_password = os.getenv("MONGO_PASSWORD", "example")
        mongo_host = os.getenv("MONGO_HOST", "faceverification.qp2ckht.mongodb.net")
        
        print(f"Environment variables:")
        print(f"MONGO_USER: {'set' if mongo_user else 'not set'}")
        print(f"MONGO_PASSWORD: {'set' if mongo_password else 'not set'}")
        print(f"MONGO_HOST: {mongo_host}")
        print(f"Attempting connection with: mongodb+srv://{mongo_user}:*****@{mongo_host}")
        
        self.client = MongoClient(
            f"mongodb+srv://{mongo_user}:{mongo_password}@{mongo_host}/"
            f"?retryWrites=true&w=majority&appName=faceverification",
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            serverSelectionTimeoutMS=5000
        )
        
        # Test the connection immediately
        try:
            self.client.server_info()
            print("✓ Database connection verified")
        except Exception as e:
            print(f"✗ Connection failed: {str(e)}")
            raise ValueError(f"Failed to connect to MongoDB: {str(e)}")

        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.attendance_collection = self.db['attendance']
        
        # Create schema validation and indexes
        self._setup_database()

    def _setup_database(self):
        """Setup database indexes (skip schema validation for Atlas)"""
        # Only create indexes if they don't exist
        existing_indexes = self.collection.index_information()
        if 'militaryID_1' not in existing_indexes:
            index1 = IndexModel([('militaryID', pymongo.ASCENDING)], unique=True)
            self.collection.create_indexes([index1])

    def record_attendance(self, militaryID, status):
        """Record employee attendance with timestamp"""
        attendance_record = {
            "militaryID": militaryID,
            "status": status,
            "timestamp": datetime.now()
        }
        self.attendance_collection.insert_one(attendance_record)

    def delete_employee_attendance(self, militaryID):
        """Delete all attendance records for a specific employee"""
        result = self.attendance_collection.delete_many({"militaryID": militaryID})
        return result.deleted_count

    def delete_daily_attendance(self, date):
        """Delete all attendance records for a specific date"""
        start_date = datetime(date.year, date.month, date.day)
        end_date = datetime(date.year, date.month, date.day, 23, 59, 59)
        result = self.attendance_collection.delete_many({
            "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }
        })
        return result.deleted_count

    def get_all_employees(self):
        """Get all employee records from the database"""
        employees = list(self.collection.find({}))
        # Ensure all required fields exist in each record
        for emp in employees:
            emp.setdefault('rank', 'N/A')
            emp.setdefault('fullname', 'Unknown')
            emp.setdefault('militaryID', 0)
            emp.setdefault('department', 'N/A')
            emp.setdefault('image_path', '')
        return employees

    def get_attendance_by_date(self, date):
        """Get all attendance records for a specific date"""
        start_date = datetime(date.year, date.month, date.day)
        end_date = datetime(date.year, date.month, date.day, 23, 59, 59)
        return list(self.attendance_collection.find({
            "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }
        }))

    def get_attendance_by_employee(self, militaryID):
        """Get all attendance records for a specific employee"""
        return list(self.attendance_collection.find(
            {"militaryID": militaryID}
        ).sort("timestamp", pymongo.DESCENDING))

    def delete_employee(self, militaryID):
        """Delete an employee record, their attendance data, and associated image"""
        # First get the employee record to find image path
        employee = self.collection.find_one({"militaryID": militaryID})
        
        if not employee:
            return f"No employee found with ID {militaryID}"
            
        image_path = employee.get('image_path', '')
        deleted_image = False
        
        # Delete the image file if it exists
        if image_path:
            try:
                import os
                if os.path.exists(image_path):
                    os.remove(image_path)
                    deleted_image = True
            except Exception as e:
                print(f"Error deleting image: {e}")
        
        # Delete employee record
        employee_result = self.collection.delete_one({"militaryID": militaryID})
        
        # Delete attendance records
        attendance_result = self.attendance_collection.delete_many({"militaryID": militaryID})
        
        message = f"Successfully deleted employee {militaryID} and {attendance_result.deleted_count} attendance records"
        if deleted_image:
            message += " (image deleted)"
        elif image_path:
            message += " (image not found)"
            
        return message

    def add_employee(self, rank, fullname, militaryID, department, image_path):
        """Add a new employee record to the database"""
        employee_data = {
            'rank': rank,
            'fullname': fullname,
            'militaryID': militaryID,
            'department': department,
            'image_path': image_path
        }
        
        try:
            self.collection.insert_one(employee_data)
            return f"Successfully added employee {fullname} (ID: {militaryID})"
        except DuplicateKeyError:
            return f"Employee with ID {militaryID} already exists"
        except Exception as e:
            return f"Error adding employee: {str(e)}"

    def update_employee(self, militaryID, update_data):
        """Update an existing employee record"""
        try:
            # Check if employee exists
            employee = self.collection.find_one({"militaryID": militaryID})
            if not employee:
                return f"No employee found with ID {militaryID}"
            
            # Perform the update
            result = self.collection.update_one(
                {"militaryID": militaryID},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return f"Successfully updated employee {militaryID}"
            return f"No changes made to employee {militaryID}"
        except Exception as e:
            return f"Error updating employee: {str(e)}"
