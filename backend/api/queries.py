from rest_framework.views import APIView
from django.http import JsonResponse
from pymongo import MongoClient
from kafka import KafkaProducer
import json

producer = KafkaProducer(bootstrap_servers='localhost:29092')
client = MongoClient('localhost', 27017)
db = client.SRAS
attempts = db.attempts


class LoginApiView(APIView):
    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        attempt = attempts.insert_one({"status": "auth"}).inserted_id
        body["_id"] = str(attempt)
        body["type"] = "login"
        producer.send('auth', json.dumps(body).encode('utf-8'))

        while True:
            attempt_val = attempts.find_one({"_id": attempt})
            if attempt_val is None:
                return JsonResponse({'message': 'Attempt not found'}, )
            if attempt_val["status"] == "invalid":
                return JsonResponse({'message': 'Invalid credentials'}, )
            if attempt_val["status"] == "valid":
                return JsonResponse({'message': 'Success!'}, )


class SignUpApiView(APIView):
    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        attempt = attempts.insert_one({"status": "auth"}).inserted_id

        body["_id"] = str(attempt)
        body["type"] = "signup"
        # {'username': 'miunmn', 'password': '1234567', 'email': 'esteban.principe@utec.edu.pe', 'gender': '', 'video': 'https://bigdata-2022-utec-antispoofing-project.s3-us-east-2.amazonaws.com/signup-miunmn-1669704119436.webm', 'fileName': 'signup-miunmn-1669704119436.webm'}
        producer.send('auth', json.dumps(body).encode('utf-8'))

        while True:
            attempt_val = attempts.find_one({"_id": attempt})
            reason = attempt_val.get("reason", "")

            if attempt_val is None:
                return JsonResponse({'message': 'Attempt not found'}, )
            if attempt_val["status"] == "invalid":
                return JsonResponse({'message': "Invalid credentials: {}".format(reason)}, )
            if attempt_val["status"] == "valid":
                return JsonResponse({'message': 'Success!'}, )
