from django.urls import path
from .views import ReturnUrlView 

urlpatterns = [
    path('webhook/', ReturnUrlView.as_view(), name='return-url-webhook'),
]
