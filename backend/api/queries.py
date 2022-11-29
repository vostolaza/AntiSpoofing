from rest_framework.views import APIView
from django.http import JsonResponse
import json
class LoginApiView(APIView):
    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        print(body)
        
        return JsonResponse({'message': 'Hello, World!'}, )


class SignUpApiView(APIView):
    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        print(body)
        # {'username': 'miunmn', 'password': '1234567', 'email': 'esteban.principe@utec.edu.pe', 'gender': '', 'video': 'https://bigdata-2022-utec-antispoofing-project.s3-us-east-2.amazonaws.com/signup-miunmn-1669704119436.webm', 'fileName': 'signup-miunmn-1669704119436.webm'}

        retorno = {'message': 'Hello, World!'}
        return JsonResponse({'message': 'Hello, World!', 'data': retorno['message']}, status=200)