from django.urls import path
from . import queries

urlpatterns = [
    path('signup', queries.SignUpApiView.as_view()),
    path('login', queries.LoginApiView.as_view()),
]