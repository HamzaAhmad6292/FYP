import sys
import os
print("sys")
print(os.path.dirname)
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
# from elevenlabs import Client, VoiceSettings
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
# from ..sales_agent.sales_conversation import SalesConversation
from ..sales_agent.sales_conversation import SalesConversation
sepr = "\n===============================================\n"
app = Flask(__name__)
CORS(app) 


# Enable CORS for all routes
# # Initialize Eleven Labs API client
# eleven_client = Client(api_key=os.environ.get("ELEVEN_API_KEY"))


load_dotenv()


sales_bot=SalesConversation()

eleven_client = ElevenLabs(api_key=os.getenv("eleven_labs_key"),)

@app.route('/transcription', methods=['POST'])
def transcription():
    data = request.json
    transcription_text = data['text']
    
    print(sepr, "Rcvd:", transcription_text, sepr)


    print(sepr, "Sending req to groq API ", sepr)
    response_text = sales_bot.process_message(transcription_text)

    # Convert the response to audio using Eleven Labs TTS
    # audio_url = tts(response_text)
    # # Print Groq API response
    # print("Groq API Response:", response_text)
    # return jsonify({
    #     'message': 'Transcription received successfully', 
    #     'groq_response': response_text,
    #     'audio_url': audio_url
    # })

    return jsonify({
        'message': 'Transcription received successfully', 
        'groq_response': response_text,
        # 'audio_url': audio_url
    })





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
    
    audio_file_path = os.path.join('static', 'response_audio.mp3')
    
    with open(audio_file_path, 'wb') as f:
        for chunk in response: 
            f.write(chunk)

    return f'/static/response_audio.mp3'  

if __name__ == '__main__':
    app.run(debug=True)
