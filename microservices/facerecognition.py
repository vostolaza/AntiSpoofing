import json
import cv2
import face_recognition
import torch
from kafka import KafkaConsumer, KafkaProducer
from pymongo import MongoClient

consumer = KafkaConsumer(
    'faceRecognition', bootstrap_servers='localhost:29092')
producer = KafkaProducer(bootstrap_servers='localhost:29092')

client = MongoClient('localhost', 27017)

db = client.SRAS

attempts = db.attempts


def getFramesFromVideo(video, samples_per_video=16, dim=128):
    frames = []
    cap = cv2.VideoCapture(video)
    resampling_rate = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT) / samples_per_video)
    count = 0
    failed = False
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
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


def compareFrames(original, login):
    count = 0
    for frame in login:
        if face_recognition.compare_faces(original, frame)[0]:
            count += 1
    return count/len(login) >= 0.8


for event in consumer:
    data = json.loads(event.value)
    attempt = attempts.find_one({"_id": data["_id"]})
    if attempt is None:
        producer.send('issues', "Attempt not found")

    # TODO: Get videos from S3
    originalVideo = "video.mp4"
    originalFrames = getFramesFromVideo(originalVideo)
    loginVideo = "video.mp4"
    loginFrames = getFramesFromVideo(loginVideo)

    videosMatch = compareFrames(originalFrames, loginFrames)
    if videosMatch:
        attempts.update_one({"_id": data["_id"]}, 
                            {"$set": {
                                "status": "valid"}})
        producer.send(
            'success', f'Successfully logged in user {data["username"]}')
    else:
        attempts.update_one({"_id": data["_id"]}, 
                            {"$set": {
                                "status": "invalid",
                                "reason": "faceRecognition"}})
        producer.send('issues', f'Facerecognition: failed to log in user {data["username"]} because faces do not match')