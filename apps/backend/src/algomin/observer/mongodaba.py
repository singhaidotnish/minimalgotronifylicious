# system modules
import json
import subprocess
from pymongo import MongoClient

# custom modules
from .base_observer import BaseObserver
from .logger import LoggerObserver
from .alert import AlertObserver

# Concrete Observer: Stores messages in MongoDB
class MongoDBObserver(BaseObserver):
    def __init__(self, db_name="websocketDB", collection_name="messages"):
        self.client = self.run_mongodb()
        self.db = self.client[db_name]  # Select database
        self.collection = self.db[collection_name]  # Select collection
        # Integrating other observers
        self.logger_observer = LoggerObserver()
        self.alert_observer = AlertObserver()
        self.logger_observer.update(f'+++ client: {self.client}, db: {self.db}, collection: {self.collection}')

    def is_mongodb_running(self):
        """Check if MongoDB is running using systemctl status."""
        try:
            subprocess.run(["systemctl", "is-active", "--quiet", "mongod"], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def start_mongodb(self):
        """Start MongoDB service if not running."""
        try:
            print("Starting MongoDB...")
            subprocess.run(["sudo", "systemctl", "start", "mongod"])
            time.sleep(5)  # Give MongoDB time to start
            return True
        except subprocess.CalledProcessError:
            return False

    def stop_mongodb(self):
        print("Stopping MongoDB...")
        pass

    def run_mongodb(self):
        # Ensure MongoDB is running
        if not self.is_mongodb_running():
            self.start_mongodb()
        else:
            print('+++ ✅ Already running ')

        # Connect to MongoDB
        try:
            client = MongoClient("mongodb://localhost:27017/")
            print("Connected to MongoDB successfully!")
            print("Databases:", client.list_database_names())
        except Exception as e:
            print("Failed to connect to MongoDB:", e)
        return client

    def update(self, message):
        data = json.loads(message)
        self.collection.insert_one(data)  # Store message in MongoDB
        print("✅ [MongoDB] Stored message:", data)

        # Check for alert condition
        self.alert_observer.update(message)

    def get_all_messages(self):
        """Fetch all stored messages from MongoDB."""
        return list(self.collection.find({}, {"_id": 0}))  # Exclude MongoDB's default '_id' field

