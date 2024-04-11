"""
Url endpoints to interact with the chatbot.
"""

from django.urls import path
from . import views

urlpatterns = [
    path("",views.chat,name="chatbot api"),
]
