from kafka import KafkaConsumer
from kafka import KafkaProducer
from pymongo import MongoClient
from bson.objectid import ObjectId
import json

consumer = KafkaConsumer('auth', bootstrap_servers='localhost:29092',
                         auto_offset_reset='earliest', enable_auto_commit=True, group_id='my-group')
producer = KafkaProducer(bootstrap_servers='localhost:29092')

client = MongoClient('localhost', 27017)

db = client.SRAS

auth = db.auth
attempts = db.attempts


def login(data):
    username, password = data["username"], data["password"]
    if data["username"] == username and data["password"] == password:
        attempts.update_one({"_id": data["_id"]},
                            {"$set": {
                                "status": "antiSpoofing"}})
        producer.send('antiSpoofing', json.dumps(data).encode('utf-8'))
    else:
        attempts.update_one({"_id": data["_id"]},
                            {"$set": {
                                "status": "invalid",
                                "reason": "auth"}})
        producer.send(
            'issues', json.dumps({"message": f'Auth: invalid credentials for user {username}'}).encode('utf-8'))


def signup(data):
    username, email = data["username"], data["email"]
    if auth.find_one({"username": username}) is None and auth.find_one({"email": email}) is None:
        attempts.update_one({"_id": data["_id"]},
                            {"$set": {
                                "status": "antiSpoofing"}})
        print("Sending to antiSpoofing")
        producer.send('antiSpoofing', json.dumps(data).encode('utf-8'))
    else:
        attempts.update_one({"_id": data["_id"]},
                            {"$set": {
                                "status": "invalid",
                                "reason": "auth"}})
        print("Sending to issues")
    producer.send(
        'issues', json.dumps({"message": f'Auth: user {username} cannot be created because already exists'}).encode('utf-8'))


for event in consumer:
    data = json.loads(event.value)
    print("Attempt", data["_id"])
    attempt = attempts.find_one({"_id": ObjectId(data["_id"])})
    if attempt is None:
        producer.send('issues', json.dumps(
            {'message': 'Auth: attempt not found'}).encode('utf-8'))
    else:
        print("Found attempt")
        if data["type"] == "login":
            print("Login")
            login(data)
        elif data["type"] == "signup":
            print("Signup")
            signup(data)
