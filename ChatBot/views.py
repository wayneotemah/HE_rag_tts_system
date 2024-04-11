from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging


@api_view(["GET"])
def chat(request):
    """
    This function is used to interact with the chatbot.
    """
    try:
        response = {
            "message": "Welcome to the chatbot API"
        }
        return Response(response,status=status.HTTP_200_OK)
    except Exception as e:
        logging.exception(e)
        return Response({"message":"An error occurred"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)