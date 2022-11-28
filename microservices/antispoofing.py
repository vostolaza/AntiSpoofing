from kafka import KafkaConsumer
from kafka import KafkaProducer
from pymongo import MongoClient
import torch
import json
import cv2

consumer = KafkaConsumer('antiSpoofing', bootstrap_servers='localhost:29092')
producer = KafkaProducer(bootstrap_servers='localhost:29092')

client = MongoClient('localhost', 27017)

db = client.SRAS

auth = db.auth
attempts = db.attempts


def getFramesFromVideo(video, samples_per_video=16, dim=128):
    frames = []
    cap = cv2.VideoCapture(video)
    resampling_rate = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT) / samples_per_video)
    count = 0
    failed = False
    face_cascade = cv2.CascadeClassifier('../haarcascade_frontalface_default.xml')
    while cap.isOpened():
        success, img = cap.read()
        if success and (failed or (count % resampling_rate == 0)):
            faces = face_cascade.detectMultiScale(
                cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 1.1, 4)
            if len(faces) != 1:
                failed = True
                continue
            (x, y, w, h) = faces[0]
            frames.append(torch.Tensor(cv2.resize(
                img[y:y+h, x:x+w], dsize=(dim, dim))))
            failed = False
        else:
            break
        count += 1
    return torch.stack(frames).permute(0, 3, 1, 2)


def evaluateVideo(frames):
    model = torch.load("../model.pkl")
    with torch.no_grad():
        outputs = model(frames)

    valid = 0
    invalid = 0
    for output in outputs:
        if output[0] > output[1]:
            invalid += 1
        else:
            valid += 1
    return valid > invalid


for event in consumer:
    data = json.loads(event.value)
    attempt = attempts.find_one({"_id": data["_id"]})
    if attempt is None:
        producer.send('issues', "Spoofing: attempt not found")

    # TODO: Get video from S3
    video = "video.mp4"
    frames = getFramesFromVideo(video)

    realVideo = evaluateVideo(frames)

    if data["type"] == "signup":
        if realVideo:
            auth.insert_one({"username": data["username"], "password": data["password"],
                        "email": data["email"], "gender": data["gender"]})
            attempts.update_one({"_id": data["_id"]}, 
                            {"$set": 
                                {"status": "valid"}})
            producer.send('success', f'User {data["username"]} successfully created')
        else:
            attempts.update_one({"_id": data["_id"]}, 
                            {"$set": {
                                "status": "invalid", 
                                "reason": "spoofing"}})
            producer.send('issues', f'Spoofing: user {data["username"]} cannot be created')

    elif data["type"] == "login":
        if realVideo:
            attempts.update_one({"_id": data["_id"]}, {
                            "$set": {"status": "faceRecognition"}})
            producer.send('faceRecognition', event.value)
        else:
            attempts.update_one({"_id": data["_id"]}, {
                            "status": "invalid", "reason": "spoofing"})
            producer.send('issues', f'Spoofing: user {data["username"]} cannot be logged in')