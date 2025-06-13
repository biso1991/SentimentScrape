from pymongo import MongoClient
from config import LABEL_MAP

def export_train_data(filename="train_data.txt"):
    mongo_client = MongoClient("mongodb://mongoadmin:mongopass@mongodb:27017/")
    db = mongo_client["tweetdb"]
    collection = db["tweets"]
    data = list(collection.find({"sentiment": {"$in": list(LABEL_MAP.keys())}}))
    with open(filename, "w", encoding="utf-8") as f:
        for d in data:
            f.write(f"{d['cleaned']}\t{d['sentiment']}\n")
    print(f"Extracted {len(data)} labeled tweets to {filename}")