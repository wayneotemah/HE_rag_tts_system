"""
Url endpoints to interact with the chatbot.
"""

from django.urls import path
from . import views

urlpatterns = [
    path("text/",views.chat,name="chat api"),
    path("voice/",views.voice_chat,name="voice api"),
]
