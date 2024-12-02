from django.urls import path
from .views import MessageWebhookView

urlpatterns = [
    path('webhook/', MessageWebhookView.as_view(), name='message-webhook'),
]

