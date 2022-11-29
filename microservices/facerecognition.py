import json
import numpy as np
import cv2
import face_recognition
import torch
from kafka import KafkaConsumer, KafkaProducer
from pymongo import MongoClient
from bson.objectid import ObjectId

consumer = KafkaConsumer(
    'faceRecognition', bootstrap_servers='localhost:29092', auto_offset_reset='earliest', enable_auto_commit=True, group_id='my-group')
producer = KafkaProducer(bootstrap_servers='localhost:29092')

client = MongoClient('localhost', 27017)

db = client.SRAS

attempts = db.attempts
auth = db.auth


def getFramesFromVideo(video, samples_per_video=16, dim=128):
    frames = []
    cap = cv2.VideoCapture(video)
    resampling_rate = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT) / samples_per_video)
    count = 0
    failed = False
    face_cascade = cv2.CascadeClassifier(
        '../haarcascade_frontalface_default.xml')
    while cap.isOpened():
        success, img = cap.read()
        if success and (failed or (count % resampling_rate == 0)):
            faces = face_cascade.detectMultiScale(
                cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 1.1, 4)
            if len(faces) != 1:
                failed = True
                continue
            (x, y, w, h) = faces[0]
            frames.append(cv2.resize(
                img[y:y+h, x:x+w], dsize=(dim, dim)))
            failed = False
        else:
            break
        count += 1
    return frames


def compareFrames(original, login):
    login = face_recognition.face_encodings(login[0])[0]
    original = face_recognition.face_encodings(original[0])[0]
    comp = face_recognition.compare_faces([original], login)

    return comp[0]


for event in consumer:

    data = json.loads(event.value)
    attempt = attempts.find_one({"_id": ObjectId(data["_id"])})
    if attempt is None:
        producer.send('issues', json.dumps(
            {"message": "Attempt not found"}).encode('utf-8'))

    user = auth.find_one({"username": data["username"]})
    originalVideo = ""
    if user is not None:
        originalVideo = user["video"]
    print('originalVideo', originalVideo)
    originalFrames = getFramesFromVideo(originalVideo)
    loginVideo = data["video"]
    loginFrames = getFramesFromVideo(loginVideo)

    videosMatch = compareFrames(originalFrames, loginFrames)
    if videosMatch:
        attempts.update_one({"_id": ObjectId(data["_id"])},
                            {"$set": {
                                "status": "valid"}})
        print("logged in user", data["username"])
        producer.send(
            'success', json.dumps({"message": f'Successfully logged in user {data["username"]}'}).encode('utf-8'))
    else:
        attempts.update_one({"_id": ObjectId(data["_id"])},
                            {"$set": {
                                "status": "invalid",
                                "reason": "faceRecognition"}})
        print("failed to log in user", data["username"])
        producer.send(
            'issues', json.dumps({"message": f'Facerecognition: failed to log in user {data["username"]} because faces do not match'}).encode('utf-8'))
