from kafka import KafkaProducer
from pymongo import MongoClient
import json


producer = KafkaProducer(
    bootstrap_servers='localhost:29092')

client = MongoClient('localhost', 27017)
db = client.SRAS
attempts = db.attempts


for i in range(40, 50):
    attempt = attempts.insert_one({"status": "auth"}).inserted_id
    print("attempt", attempt)
    username = f"TestUser{i}"
    password = f"TestPassword{i}"
    email = f"TestEmail{i}"
    gender = f"TestGender{i}"
    data = {
        "_id": str(attempt),
        "username": username,
        "password": password,
        "email": email,
        "gender": gender,
        "type": "login",
        "video": "../CASIA_faceAntisp/train_release/1/2.avi",
        "m": i
    }
    producer.send('auth', json.dumps(data).encode('utf-8'))
    print("Sent")
