from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "LibraryDB"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    client.admin.command("ping")
    db = client[DB_NAME]
    admins = db["admins"]
    books = db["books"]
    students = db["students"]
    issued_books = db["issued_books"]

    if admins.count_documents({}) == 0:
        admins.insert_one({"username": "admin", "password": "admin123"})
except ConnectionFailure:
    client = None
    db = admins = books = students = issued_books = None
