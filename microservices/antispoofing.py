from kafka import KafkaConsumer
from kafka import KafkaProducer
from pymongo import MongoClient
from bson.objectid import ObjectId
import torch.nn as nn
import torch
import json
import cv2


class CNN(nn.Module):
    def __init__(self, num_classes=10):
        super(CNN, self).__init__()
        self.layer1 = nn.Sequential(
            nn.Conv2d(in_channels=3, out_channels=16,
                      kernel_size=3, stride=1, padding=2),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2))
        self.layer2 = nn.Sequential(
            nn.Conv2d(16, 32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2))
        self.layer3 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=7, stride=1, padding=3),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2))
        self.layer4 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=11, stride=1, padding=5),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2))
        self.fc = nn.Linear(8192, num_classes)

    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = out.reshape(out.size(0), -1)
        out = self.fc(out)
        return out


consumer = KafkaConsumer('antiSpoofing', bootstrap_servers='localhost:29092',
                         auto_offset_reset='earliest', enable_auto_commit=True, group_id='my-group')
producer = KafkaProducer(bootstrap_servers='localhost:29092')

client = MongoClient('localhost', 27017)

db = client.SRAS

auth = db.auth
attempts = db.attempts

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


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
            frames.append(torch.Tensor(cv2.resize(
                img[y:y+h, x:x+w], dsize=(dim, dim))))
            failed = False
        else:
            break
        count += 1
    return torch.stack(frames).permute(0, 3, 1, 2)


def evaluateVideo(frames):
    model = torch.load("../model.pt").to(device)
    frames = frames.to(device)
    with torch.no_grad():
        outputs = model(frames)

    print(outputs)
    valid = 0
    invalid = 0
    for output in outputs:
        if output[0] > output[1]:
            invalid += 1
        else:
            valid += 1
    print("valid frames:", valid)
    print("invalid frames:", invalid)
    return valid > invalid


def signup(data, realVideo):
    if realVideo:
        auth.insert_one({"username": data["username"], "password": data["password"],
                         "email": data["email"], "gender": data["gender"], "video": data["video"]})
        attempts.update_one({"_id": data["_id"]},
                            {"$set":
                            {"status": "valid"}})
        print("Sending to success")
        producer.send(
            'success', json.dumps({"message": f'User {data["username"]} successfully created'}).encode('utf-8'))
    else:
        attempts.update_one({"_id": data["_id"]},
                            {"$set": {
                                "status": "invalid",
                                "reason": "spoofing"}})
        print("Sending to issues")
        producer.send(
            'issues', json.dumps({"message": f'Spoofing: user {data["username"]} cannot be created'}).encode('utf-8'))


def login(data, realVideo):
    if realVideo:
        attempts.update_one({"_id": data["_id"]}, {
            "$set": {"status": "faceRecognition"}})
        producer.send('faceRecognition', json.dumps(data).encode('utf-8'))
    else:
        attempts.update_one({"_id": data["_id"]}, {
            "$set": {"status": "invalid", "reason": "spoofing"}})
        producer.send(
            'issues', json.dumps({"message": f'Spoofing: user {data["username"]} cannot be logged in'})).encode('utf-8')


for event in consumer:
    data = json.loads(event.value)
    print("In antiSpoofing")
    attempt = attempts.find_one({"_id": ObjectId(data["_id"])})
    if attempt is None:
        producer.send('issues', json.dumps(
            {"message": "Spoofing: attempt not found"}).encode('utf-8'))
    print("Found attempt")
    video = data["video"]
    frames = getFramesFromVideo(video)
    print("Got frames: ", frames.shape)
    realVideo = evaluateVideo(frames)
    print("Evaluated video: ", realVideo)
    if data["type"] == "signup":
        signup(data, realVideo)
    elif data["type"] == "login":
        login(data, realVideo)
