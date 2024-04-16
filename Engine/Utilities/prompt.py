import requests
import os
import uuid
import logging
from dotenv import load_dotenv
from langchain.prompts import HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from django.conf import settings
from Engine.Utilities.prompt_messages import SysMessage
from Engine.Utilities.vdb_init import doc_search_service



load_dotenv()
logger = logging.getLogger(__name__)

def TTS_API(text):
    # Constants for the script
    CHUNK_SIZE = 1024 # Size of chunks to read/write at a time
    XI_API_KEY = os.getenv("XI_API_KEY","") # Your API key for authentication
    VOICE_ID = os.getenv("VOICE_ID","") # ID of the voice model to use
    OUTPUT_DIR = os.path.join(settings.MEDIA_ROOT, "Voice") # Directory to save the output audio file

    # Ensure the output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Generate a unique UUID for the audio file name
    audio_file_name = f"{uuid.uuid4()}.mp3"
    OUTPUT_PATH = os.path.join(OUTPUT_DIR, audio_file_name)

    # Construct the URL for the Text-to-Speech API request
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"

    # Set up headers for the API request, including the API key for authentication
    headers = {
        "Accept": "application/json",
        "xi-api-key": XI_API_KEY
    }

    # Set up the data payload for the API request, including the text and voice settings
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 1.0,
            "style": 0.63,
            "use_speaker_boost": True
        }
    }

    # Make the POST request to the TTS API with headers and data, enabling streaming response
    response = requests.post(tts_url, headers=headers, json=data, stream=True)

    # Check if the request was successful
    if response.ok:
        # Open the output file in write-binary mode
        with open(OUTPUT_PATH, "wb") as f:
            # Read the response in chunks and write to the file
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
        # Inform the user of success
        print("Audio stream saved successfully.")
        # Return the URL and the text
        return f"{settings.MEDIA_URL}Voice/{audio_file_name}", text
    else:
        # Print the error message if the request was not successful
        print(response.text)
        return None, text




model = ChatOpenAI(openai_api_key=os.getenv("openai_api_key",""))

def llm_query(context:str, user_input:str)->str:
    """
    This function is used to interact with the chatbot openAI model.
    
    Args:
    context: str: The document from DocSeachService.search.
    user_input: str: The user's input.
    
    Returns:
    str: The response from the chatbot model.
    
    """
    try:
        response = None
        human_message = (
            """user's input:
            """
            + user_input
            + """
            document context:
            """
            + context
        )
        chat_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=(SysMessage)),
                HumanMessagePromptTemplate.from_template(human_message),
            ]
        )

        messages = chat_template.format_messages(
            context=context,
            user_input=user_input,
        )
        data = model.invoke(messages)
        for item in data:
            if item[0] == "content":
                response = item[1]
                break

        return response
    except Exception as e:
        logging(f"An error occurred: {e}")

def llm_answer(user_input:str)->str:
    """
    This function is used to interact with the chatbot openAI model.
    
    Args:
    user_input: str: The user's input.
    
    Returns:
    str: The response from the chatbot model.
    
    """
    context = doc_search_service.search(user_input)
    context = context[0].page_content if context else ["No context found"]
    response = llm_query(context=context, user_input=user_input)
    return response
    

def voice_answer(user_input:str)->str:
    """
    This function is used to interact with the chatbot openAI model and generate a voice response.
    
    Args:
    user_input: str: The user's input.
    
    Returns:
    str: The response from the chatbot model.
    url: str: The URL of the voice response.
    
    """
    # response = llm_answer(user_input)
    url, text = TTS_API(user_input)
    return url, text   

