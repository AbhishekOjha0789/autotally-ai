import os
from pymongo import MongoClient
import hashlib
from dotenv import load_dotenv

load_dotenv()

# Get MongoDB URI from environment variables (e.g., MongoDB Atlas connection string)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["autotally_ai"]

users_collection = db["users"]
receipts_collection = db["receipts"]

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register_user_db(username: str, password: str):
    username = username.strip()
    if users_collection.find_one({"username": username}):
        return False, "Username already exists."
    
    user_doc = {
        "username": username,
        "password_hash": hash_password(password)
    }
    result = users_collection.insert_one(user_doc)
    return True, str(result.inserted_id)

def authenticate_user_db(username: str, password: str):
    username = username.strip()
    user = users_collection.find_one({"username": username})
    
    if not user or user["password_hash"] != hash_password(password):
        return False, "Invalid username or password."
    return True, str(user["_id"])