from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging
from Engine.Utilities.prompt import llm_answer,voice_answer

@api_view(["POST"])
def chat(request):
    """
    This function is used to interact with the chatbot.
    """
    
    if request.method != "POST":
        return Response({"message":"Invalid request method"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    try:
        query = request.data.get("query")

        response = llm_answer(query)
        context = {
            "response": response
        
        }
        return Response(context,status=status.HTTP_200_OK)
    except Exception as e:
        logging.exception(e)
        return Response({"message":"An error occurred" },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["POST"])
def voice_chat(request):
    """
    This function is used to interact with the chatbot with voice output.
    """
    
    if request.method != "POST":
        return Response({"message":"Invalid request method"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    try:
        query = request.data.get("query")

        voice_url,response = voice_answer(query)
        context = {
            "response": response,
            "voice": voice_url
        
        }
        return Response(context,status=status.HTTP_200_OK)
    except Exception as e:
        logging.exception(e)
        return Response({"message":"An error occurred" },status=status.HTTP_500_INTERNAL_SERVER_ERROR)