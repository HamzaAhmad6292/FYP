from flask import Flask, request, jsonify, send_from_directory, url_for
from flask_cors import CORS
import os
from groq import Groq
import sys
import os
from dotenv import load_dotenv
# from elevenlabs import Client, VoiceSettings
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

sepr = "\n===============================================\n"

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

load_dotenv()

eleven_client = ElevenLabs(api_key=os.getenv("eleven_labs_key"),)

name = ''
email = ''
phone=''
product=''
description=''

transcription_text = "" 
response = ""


# =====================================================================
# Hamza Please uncoooment this section
# Also uncomment in the transcription function

from ..sales_agent.sales_conversation import SalesConversation
sales_bot=SalesConversation()
# =====================================================================



# =====================================================================
# ====================        Routes       ============================
# =====================================================================
# This function is used to get the user info from the form
# When the user fills the form, this receives the user info
@app.route('/post-user-info', methods=['POST'])
def submit_info():
    global name, email,phone,product,description
    data = request.json  # Access JSON data from the POST request
    print(data)
    name = data.get('name')  
    # email = data.get('email')  
    phone = data.get('phone') 
    product = data.get('product')  
    description = data.get('description')  

    print(sepr, f"Received Info: \nName: {name} \nPhone: {phone} \nProduct: {product} \nDescription: {description} ", sepr)

    return jsonify({
        'message': "Received Successfully"
    })
# =====================================================================

# =====================================================================
# This function is used by the front end to fetch the user's info
@app.route('/get-user-info', methods=['GET'])
def get_user_info():
    user_info = {
        "name": name,
        "phone":phone,
        "product":product,
        "description":description
    }

    print(sepr, "Sending user info to frontend", sepr)
    return jsonify(user_info)
# =====================================================================

# =====================================================================
# This function is used by the front end to fetch the response from the AI
@app.route('/get-ai-response', methods=['GET'])
def get_ai_response():
    resp = {
        "text":response
    }

    print(sepr, "Sending AI response to frontend", sepr)
    return jsonify(resp)
# =====================================================================

# =====================================================================
# This is the main function that takes care of the following 
# - transcription (using google webkit)
# - send req to groq API 
# - text-to-speech using eleven labs API
@app.route('/transcription', methods=['POST'])
def transcription():
    global transcription_text
    data = request.json
    transcription_text = data['text']
    
    print(sepr, "Received Transcription :", transcription_text, sepr)

    # print(sepr, "Sending req to groq API ", sepr)
    # response_text = sales_bot.process_message(transcription_text)

    # # Convert the response to audio using Eleven Labs TTS
    # audio_url = tts(response_text)

    # # Print Groq API response
    # print("Groq API Response:", response_text)
    
    # return jsonify({
    #     'message': 'Transcription received successfully', 
    #     'groq_response': response_text,
    #     'audio_url': audio_url
    # })


    audio_url = url_for('static', filename='response_audio.mp3', _external=True)
    response_text = sales_bot.process_message(transcription_text)
    
    return jsonify({
        # 'message': 'Transcription received successfully, hi ya', 
        'message': response_text,
        'audio_url': audio_url
    })
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

    # Define the path to save the audio file in the static directory
    audio_file_path = os.path.join('static', 'response_audio.mp3')
    
    with open(audio_file_path, 'wb') as f:
        for chunk in response:  # Iterate over the generator to write chunks
            f.write(chunk)

    # Return the URL to access the audio
    return f'/static/response_audio.mp3'  # URL path
# =====================================================================






if __name__ == '__main__':
    app.run(debug=True)






