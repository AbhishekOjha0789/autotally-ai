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
products_collection = db["products"]  # <-- New collection for store inventory

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

# --- NEW POS INVENTORY & CHECKOUT FUNCTIONS ---

def get_product_by_barcode(barcode: str):
    """Fetch product details and stock level by barcode."""
    product = products_collection.find_one({"barcode": barcode.strip()}, {"_id": 0})
    return product

def seed_sample_products():
    """Helper to seed initial mock inventory if empty."""
    if products_collection.count_documents({}) == 0:
        sample_products = [
            {"barcode": "890103054212", "name": "Aashirvaad Atta 10kg", "price": 420.0, "stock": 50},
            {"barcode": "890145001234", "name": "Tata Salt 1kg", "price": 28.0, "stock": 100},
            {"barcode": "890251900128", "name": "Surf Excel Detergent 1kg", "price": 145.0, "stock": 30}
        ]
        products_collection.insert_many(sample_products)

# Run once on startup to ensure sample products exist for testing
seed_sample_products()

def process_pos_checkout(user_id: str, company_name: str, vendor_name: str, items: list):
    """
    Processes checkout: decrements stock from inventory and records the transaction/XML history.
    """
    # 1. Verify and decrement stock for each item
    for item in items:
        barcode = item["barcode"]
        qty_purchased = item["quantity"]
        
        prod = products_collection.find_one({"barcode": barcode})
        if not prod or prod["stock"] < qty_purchased:
            return False, f"Insufficient stock or product missing for barcode: {barcode}"
            
        # Decrement stock
        products_collection.update_one(
            {"barcode": barcode},
            {"$inc": {"stock": -qty_purchased}}
        )
    
    # 2. Generate Tally XML (or store receipt log)
    receipt_doc = {
        "user_id": user_id,
        "company_name": company_name,
        "vendor_name": vendor_name,
        "items": items,
        "created_at": hashlib.sha256(str(items).encode()).hexdigest()[:10] # placeholder or timestamp
    }
    receipts_collection.insert_one(receipt_doc)
    
    return True, "Checkout successful"