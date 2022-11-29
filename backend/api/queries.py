from rest_framework.views import APIView
from django.http import JsonResponse

class LoginApiView(APIView):
    def post(self, request):
        return JsonResponse({'message': 'Hello, World!'}, )


class SignUpApiView(APIView):
    def post(self, request):
        retorno = {'message': 'Hello, World!'}
        return JsonResponse({'message': 'Hello, World!', 'data': retorno['message']}, status=200)