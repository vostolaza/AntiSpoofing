from kafka import KafkaConsumer
from kafka import KafkaProducer
from pymongo import MongoClient
import json

consumer = KafkaConsumer('auth', bootstrap_servers='localhost:29092')
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
        producer.send('antiSpoofing', event.value)
    else:
        attempts.update_one({"_id": data["_id"]}, 
                            {"$set": {
                                "status": "invalid",
                                "reason": "auth"}})
        producer.send('issues', f'Auth: invalid credentials for user {username}')


def signup(data):
    username, password = data["username"], data["password"], data["email"]
    if auth.find_one({"username": username}) is None and auth.find_one({"email": password}) is None:
        attempts.update_one({"_id": data["_id"]}, 
                            {"$set": {
                                "status": "antiSpoofing"}})
        producer.send('antiSpoofing', event.value)
    else:
        attempts.update_one({"_id": data["_id"]}, 
                            { "$set": {
                                "status": "invalid",
                                "reason": "auth"}})
        producer.send('issues', f'Auth: user {username} cannot be created because already exists')


for event in consumer:
    data = json.loads(event.value)
    attempt = attempts.find_one({"_id": data["_id"]})
    if attempt is None:
        producer.send('issues', "Auth: attemp not found")
        
    if data["type"] == "login":
        login(data)
    elif data["type"] == "signup":
        signup(data)
