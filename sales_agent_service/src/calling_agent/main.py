from flask import Flask, request, Response, send_from_directory
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from flask import jsonify

import os
from typing import Optional

from src.sales_agent.sales_conversation import SalesConversation

app = Flask(__name__)
app.static_folder = "src/calling_agent/static"

# =====================================================================
# =====================================================================
# =====================================================================
# Please use the following command to run this file from the root directory
# i.e sales_agent_service
# python3 -m src.calling_agent.main
# You also need to have a publically exposed URL 
# 1 - start the ngrok server 
# 2 - Expose the port using NGROK 
# 3 - Copy the public URL in the /make_call
# 4 - Initiate the call by hitting that ip address using CURL command or browser
# Example : https://8e6c-39-63-130-153.ngrok-free.app/make_call
# Make sure that you dont forget writing "/make_call" at the end of the URL
# =====================================================================
# =====================================================================
# =====================================================================


# eleven_client = ElevenLabs(api_key=os.getenv("eleven_labs_key"))

# Base URL for your public-facing server
PUBLIC_URL = "https://fc9c-39-46-254-90.ngrok-free.app"

# Twilio Client
# client = Client(account_sid, auth_token)

sales_bot = SalesConversation()

# =====================================================================
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


def tts(text: str) -> str:
    # Make sure the static directory exists
    os.makedirs("src/calling_agent/static", exist_ok=True)
    
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
    delete_file("src/calling_agent/static", "response_audio.mp3")

    audio_file_path = os.path.join('src/calling_agent/static', 'response_audio.mp3')
    print("Saving audio to (Relative Path):",audio_file_path)
    print(f"Saving audio to (Absolute Path): {os.path.abspath(audio_file_path)}")  # Print absolute path

    with open(audio_file_path, 'wb') as f:
        for chunk in response:  # Iterate over the generator to write chunks
            f.write(chunk)

    print("voice fetched")

    # Return the public URL to access the audio
    return f"{PUBLIC_URL}/static/response_audio.mp3"  # URL path

# =====================================================================
# =====================================================================
# =====================================================================

# Route to initiate a call
@app.route("/make_call")
def make_call():
    # Get phone number (with fallback default)
    phone_number = request.args.get('phone_number', '+92 320 0435945')
    company_data = request.args.get('company_data', '')
    customer_data = request.args.get('customer_data', '')
    product_info = request.args.get('product_info', '')
    
    global call_data
    call_data = {
        'company_data': company_data,
        'customer_data': customer_data,
        'product_info': product_info
    }

    # print(call_data)
    
    # Make the call
    call = client.calls.create(
        to=phone_number,
        from_=twilio_number,
        url=f"{PUBLIC_URL}/voice"  # Replace with your server URL
    )
    
    return {
        "message": f"Call initiated with SID: {call.sid}",
        "details": {
            "phone_number": phone_number,
            "company_data": company_data,
            "customer_data": customer_data,
            "product_info": product_info
        }
    }


# TwiML route that handles the call
@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()
    
    # Generate the greeting audio with ElevenLabs
    greeting_text = "Hello, this is an automated call. What can I help you with today?"
    # audio_url = tts(greeting_text)
    response.say(greeting_text)
    
    # Gather speech input
    gather = Gather(input='speech', action='/process_speech', timeout=3, 
                   speech_timeout='auto', language='en-US')
    response.append(gather)
    
    return Response(str(response), mimetype="application/xml")


# Route to process speech input
@app.route("/process_speech", methods=["POST"])
def process_speech():
    response = VoiceResponse()
    speech_result = request.form.get('SpeechResult', '')
    print("Speech Result : ", speech_result)
    
    # Get the response from sales bot
    answer = sales_bot.process_message(speech_result) if sales_bot else "Bot response placeholder"
    # answer = "Hamza's Bot should respond here."
    # Generate audio response with ElevenLabs
    audio_url = tts(answer)
    

    response.play(audio_url)
    
    # Gather more input
    gather = Gather(input='speech', action='/process_speech', timeout=3, 
                   speech_timeout='auto', language='en-US')
    response.append(gather)
    
    return Response(str(response), mimetype="application/xml")

# Route to serve audio files
@app.route("/static/<filename>")
def get_audio(filename):
    return send_from_directory('static', filename)



@app.route("/return_demo_api")
def demo_api():
    # Define the conversation data
    conversation = {
        "messages": [
            {
                "sender": "AI Chatbot",
                "message": "Hello! I noticed your restaurant is doing great. Have you considered using AI to automate customer reservations and feedback management?"
            },
            {
                "sender": "Restaurant Owner",
                "message": "Hey! We've been managing things manually so far. Not sure if AI is really needed for us."
            },
            {
                "sender": "AI Chatbot",
                "message": "I get that! But imagine freeing up your staff's time by letting AI handle repetitive tasks like answering FAQs and managing bookings. It can even send personalized offers to your customers!"
            },
            {
                "sender": "Restaurant Owner",
                "message": "That sounds interesting, but I'm worried about the cost. We're a small business and have a tight budget."
            },
            {
                "sender": "AI Chatbot",
                "message": "Totally understandable! Our service is affordable, and it actually helps increase revenue by improving customer retention. Plus, we offer a free trial so you can see the impact before committing!"
            },
            {
                "sender": "Restaurant Owner",
                "message": "A free trial sounds good! How does the setup work, and how long does it take?"
            }
        ]
    }
    
    # Define the action
    action = "schedule_demo"
    
    # Combine the data
    response_data = {
        "action": action,
        "conversation": conversation
    }
    
    # Return the JSON response
    return jsonify(response_data)




if __name__ == "__main__":
    # Run the Flask app
    app.run(host="0.0.0.0", port=8000, debug=True)