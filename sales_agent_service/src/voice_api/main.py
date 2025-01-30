from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
from elevenlabs import ElevenLabs
import os
from groq import Groq
import sys
import os
from requests import request
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs




# =====================================================
# =====================================================
# =====================================================
# =====================================================
# =====================================================
# =====================================================
# =====================================================
# =====================================================

# run from the root directory 
# i.e run from this directory 
# sales_agent_service 
# uvicorn src.voice_api.main:app --reload

# =====================================================
# =====================================================
# =====================================================
# =====================================================
# =====================================================
# =====================================================
# =====================================================
# =====================================================







# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()


# from ..sales_agent.sales_conversation import SalesConversation
from src.sales_agent.sales_conversation import SalesConversation


sepr = "\n===============================================\n"


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Eleven Labs client and sales bot
eleven_client = ElevenLabs(api_key=os.getenv("eleven_labs_key"))
sales_bot = SalesConversation()

# Placeholder variables
name = ''
email = ''
phone = ''
product = ''
description = ''
transcription_text = ""
response = ""


# =====================================================================
# This function is used to get the user info from the form
# When the user fills the form, this receives the user info
@app.post("/post-user-info")
async def submit_info(request: Request):

    print("\nRUNNING - /post-user-info")

    # Parse JSON data from the request body
    data = await request.json()

    # Extract information directly
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    product = data.get("product")
    description = data.get("description")

    # Print user information
    print(f"Received Info:\nName: {name}\nPhone: {phone}\nProduct: {product}\nDescription: {description}")

    # Return a JSON response
    return JSONResponse(content={
        "message": "Received Successfully"
    })
# =====================================================================

# =====================================================================
# This function is used by the front end to fetch the user's info
@app.get("/get-user-info")
async def get_user_info():

    print("\nRUNNING - /get-user-info")

    user_info = {
        "name": name,
        "phone": phone,
        "product": product,
        "description": description,
    }
    
    print(f"{sepr} Sending user info to frontend {sepr}")
    
    # Return the dictionary directly as a JSON response
    return JSONResponse(content=user_info)
# =====================================================================

# =====================================================================
# This function is used by the front end to fetch the response from the AI
@app.get("/get-ai-response")
async def get_ai_response():

    print("\nRUNNING - /get-ai-response")

    resp = {
        "text": response
    }

    print(f"{sepr} Sending AI response to frontend {sepr}")
    
    # Return JSON directly using FastAPI
    return JSONResponse(content=resp)
# =====================================================================

# =====================================================================
# This is the main function that takes care of the following 
# - transcription (using google webkit)
# - send req to groq API 
# - text-to-speech using eleven labs API
app.mount("/static", StaticFiles(directory="src/voice_api/static"), name="static")
@app.post("/transcription")
async def transcription(request: Request):

    print("\nRUNNING - /transcription")

    global transcription_text

    # Parse JSON from the request body
    data = await request.json()
    transcription_text = data.get("text")
    
    print(sepr, "Received Transcription :", transcription_text, sepr)

    # Process message and generate audio URL
    response_text = sales_bot.process_message(transcription_text) if sales_bot else "Bot response placeholder"
    audio_url_path = tts(response_text) if tts else "static/response_audio.mp3"
    
    # audio_url_path = "/src/voice_api/static/response_audio.mp3"
    # response_text = "totoototot"
    # print(f"Audio URL Path: {audio_url_path}")

    # Ensure the audio URL is properly served
    audio_url = f"http://127.0.0.1:8000/static/response_audio.mp3"

    return JSONResponse(content={
        "message": response_text,
        "audio_url": audio_url
    })

# =====================================================================

# =====================================================================

def delete_file(folder_path: str, file_name: str) -> None:
    file_path = os.path.join(folder_path, file_name)  # Combine folder path and file name
    try:
        if os.path.exists(file_path):  # Check if the file exists
            os.remove(file_path)  # Delete the file
            print(f"File '{file_name}' has been deleted.")
        else:
            print(f"File '{file_name}' does not exist in the folder.")
    except Exception as e:
        print(f"An error occurred while deleting the file: {e}")

# =====================================================================

# =====================================================================

def tts(text: str) -> str:
    response = eleven_client.text_to_speech.convert(
        voice_id="IKne3meq5aSn9XLyUdCD",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2_5",  # use the turbo model for low latency
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )
    delete_file("src/voice_api/static","response_audio.mp3")

    audio_file_path = os.path.join('src/voice_api/static', 'response_audio.mp3')
    print(audio_file_path)
    with open(audio_file_path, 'wb') as f:
        for chunk in response:  # Iterate over the generator to write chunks
            f.write(chunk)

    print("voice fetched")

    # Return the URL to access the audio
    return audio_file_path  # URL path

# =====================================================================




# run from the root directory 
# i.e run from this directory 
# sales_agent_service 
# uvicorn src.voice_api.main:app --reload
