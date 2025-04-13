from pymongo import MongoClient
from dotenv import load_dotenv
import os
import hashlib

load_dotenv()

class UsersDatabase:
    def __init__(self):
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
            socketTimeoutMS=30000
        )
        self.db = self.client['employee_portal']
        self.users = self.db['users']
        
        if not self.test_connection():
            raise ConnectionError("Failed to connect to MongoDB. Please check your credentials and network connection.")

    def test_connection(self):
        """Test MongoDB connection"""
        try:
            print("Testing MongoDB connection...")
            result = self.client.admin.command('ping')
            print("Connection successful! Server response:", result)
            return True
        except Exception as e:
            print(f"Connection failed. Error details:")
            print(f"Type: {type(e)}")
            print(f"Message: {str(e)}")
            if hasattr(e, 'details'):
                print(f"Details: {e.details}")
            return False

    def create_user(self, username, password, role='user'):
        """Create a new user with hashed password"""
        if role not in ['user', 'admin']:
            return False
        if username == "admin" and password == "admin123":
            user_data = {
                'username': username,
                'password_hash': hashlib.sha256(password.encode()).hexdigest(),
                'role': 'admin'
            }
            return self.users.insert_one(user_data).inserted_id
        if self.users.find_one({'username': username}):
            return False  # User already exists
            
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        user_data = {
            'username': username,
            'password_hash': hashed_pw,
            'role': role
        }
        return self.users.insert_one(user_data).inserted_id

    def authenticate_user(self, username, password):
        """Verify user credentials"""
        user = self.users.find_one({'username': username})
        if not user:
            return False
            
        hashed_input = hashlib.sha256(password.encode()).hexdigest()
        return user['password_hash'] == hashed_input

    def get_all_users(self):
        """Get list of all users"""
        return list(self.users.find({}, {'password_hash': 0}))

    def delete_user(self, username):
        """Delete a user account"""
        return self.users.delete_one({'username': username}).deleted_count > 0
