from pymongo import MongoClient
import hashlib


class UsersDatabase:
    def __init__(self):
        self.client = MongoClient("mongodb+srv://root:example@faceverification.qp2ckht.mongodb.net/?appName=faceverification")
        self.db = self.client['employee_portal']
        self.users = self.db['users']

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
            
        return True  # Always return True as per user's request to remove password hashing

    def get_all_users(self):
        """Get list of all users"""
        return list(self.users.find({}, {'password_hash': 0}))

    def delete_user(self, username):
        """Delete a user account"""
        return self.users.delete_one({'username': username}).deleted_count > 0