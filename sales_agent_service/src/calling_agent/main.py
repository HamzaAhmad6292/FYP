from flask import Flask, request, Response, send_from_directory
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from flask import jsonify
import time

import os
import uuid
from typing import Optional, Dict

from sales_agent.sales_conversation import SalesConversation

app = Flask(__name__)
app.static_folder = "calling_agent/static"
sepr = "="*35

# Dictionary to store active call sessions
active_calls: Dict[str, dict] = {}

# =====================================================================
# =====================================================================
# =====================================================================
# Please use the following command to run this file from the root directory
# i.e sales_agent_service/src
# python3 -m calling_agent.main
# You also need to have a publically exposed URL 
# 1 - start the ngrok server 
# 2 - Expose the port using NGROK 
# 3 - Copy the public URL in the /make_call
# 4 - Initiate the call by hitting that ip address using CURL command or browser
# Example : https://8e6c-39-63-130-153.ngrok-free.app/make_call
# Make sure that you dont forget writing "/make_call" at the end of the URL

# if you want to modify the parameters of the call : 
# https://bdf1-39-46-241-212.ngrok-free.app/make_call?phone_number=%2B92%20320%200435945
# =====================================================================
# =====================================================================
# =====================================================================

account_sid = os.getenv("Twilio_ACCOUNT_SID")
auth_token = os.getenv("Twilio_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_NUMBER")
# print("Account SID : " , account_sid)
# print("Auth Token : " , auth_token)
# print("Number : " , twilio_number)

eleven_client = ElevenLabs(api_key=os.getenv("eleven_labs_key"))
PUBLIC_URL = os.getenv("PUBLIC_URL")

# Twilio Client
client = Client(account_sid, auth_token)

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

def tts(text: str, session_id: str) -> str:
    # Make sure the static directory exists
    os.makedirs("calling_agent/static", exist_ok=True)
    
    # Use session_id to create unique audio files
    audio_filename = f"response_audio_{session_id}.mp3"

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

    # Delete previous audio file if it exists
    delete_file("calling_agent/static", audio_filename)
    audio_file_path = os.path.join('calling_agent/static', audio_filename)
    print(f"Saving audio to (Relative Path): {audio_file_path}")
    print(f"Saving audio to (Absolute Path): {os.path.abspath(audio_file_path)}")  # Print absolute path

    with open(audio_file_path, 'wb') as f:
        for chunk in response:  # Iterate over the generator to write chunks
            f.write(chunk)

    print("voice fetched")

    # Return the public URL to access the audio
    return f"{PUBLIC_URL}/static/{audio_filename}"  # URL path

# =====================================================================
# =====================================================================
# =====================================================================

# Route to initiate a call
@app.route("/make_call")
def make_call():
    # Generate a unique session ID for this call
    session_id = str(uuid.uuid4())

    # Get phone number (with fallback default)
    phone_number = request.args.get('phone_number', '+92 320 0435945')
    company_data = request.args.get('company_data', '')
    customer_data = request.args.get('customer_data', '')
    product_info = request.args.get('product_info', '')
    
    # Initialize a new sales bot for this call
    sales_bot = SalesConversation()
    
    # Store the call data and sales bot in the active calls dictionary
    active_calls[session_id] = {
        'sales_bot': sales_bot,
        'company_data': company_data,
        'customer_data': customer_data,
        'product_info': product_info
    }

    # Generate initial greeting
    tmp = "Hello"
    greeting_text = sales_bot.process_message(tmp)
    audio_url = tts(greeting_text, session_id)
    
    # Store the audio URL in the session
    active_calls[session_id]['audio_url'] = audio_url
    
    # Make the call, passing the session ID as a parameter
    call = client.calls.create(
        to=phone_number,
        from_=twilio_number,
        url=f"{PUBLIC_URL}/voice?session_id={session_id}",
        status_callback=f"{PUBLIC_URL}/call_status?session_id={session_id}",
        status_callback_event=['completed', 'busy', 'no-answer', 'failed', 'canceled'],
        status_callback_method='POST'
    )
    
    return {
        "message": f"Call initiated with SID: {call.sid}",
        "details": {
            "session_id": session_id,
            "phone_number": phone_number,
            "company_data": company_data,
            "customer_data": customer_data,
            "product_info": product_info
        }
    }


# TwiML route that handles the call
@app.route("/voice", methods=["POST"])
def voice():
    # Get the session ID from the URL parameters
    session_id = request.args.get('session_id')
    
    # Check if the session exists (should always be true for valid calls)
    if session_id not in active_calls:
        # If somehow we get here without a valid session, create a new one
        session_id = str(uuid.uuid4())
        active_calls[session_id] = {
            'sales_bot': SalesConversation(),
            'audio_url': tts("Hello, this is an automated call. What can I help you with today?", session_id)
        }
    
    response = VoiceResponse()
    
    # Play the audio for this session
    response.play(active_calls[session_id]['audio_url'])
    
    # Gather speech input, passing the session ID
    gather = Gather(input='speech', action=f'/process_speech?session_id={session_id}', 
                    timeout='auto', speech_timeout='auto', language='en-US')
    response.append(gather)
    
    return Response(str(response), mimetype="application/xml")


# Route to process speech input
@app.route("/process_speech", methods=["POST"])
def process_speech():
    # Get the session ID from the URL parameters
    session_id = request.args.get('session_id')
    
    # If the session doesn't exist, return an error message
    if session_id not in active_calls:
        response = VoiceResponse()
        response.say("Sorry, there was an error with your call. Please try again.")
        response.hangup()
        return Response(str(response), mimetype="application/xml")
    
    response = VoiceResponse()
    speech_result = request.form.get('SpeechResult', '')
    print(f"Session {session_id} - Speech Result: {speech_result}")
    
    # Get the response from this session's sales bot
    sales_bot = active_calls[session_id]['sales_bot']
    answer = sales_bot.process_message(speech_result)
    
    # Generate audio response with ElevenLabs
    audio_url = tts(answer, session_id)
    
    # Update the audio URL for this session
    active_calls[session_id]['audio_url'] = audio_url
    
    response.play(audio_url)
    
    # Gather more input
    gather = Gather(input='speech', action=f'/process_speech?session_id={session_id}', 
                   timeout=3, speech_timeout='auto', language='en-US')
    response.append(gather)
    
    print(sepr, "Response", sepr)
    return Response(str(response), mimetype="application/xml")


# Route to handle call status updates
@app.route("/call_status", methods=["POST"])
def call_status():
    # Get the session ID and call status from the request
    session_id = request.form.get('session_id')
    call_status = request.form.get('CallStatus')
    call_sid = request.form.get('CallSid')
    
    print(f"Call status update: {call_status} for session {session_id}, Call SID: {call_sid}")

    # If the call is completed or failed, clean up the session
    if call_status in ['completed', 'failed', 'busy', 'no-answer', 'canceled']:
        if session_id in active_calls:
            # Log the disconnection immediately
            print(f"⚠️ Call disconnected: {call_status} for session {session_id}, Call SID: {call_sid}")

            try:
                audio_filename = f"response_audio_{session_id}.mp3"
                delete_file("calling_agent/static", audio_filename)
            except Exception as e:
                print(f"Error cleaning up files: {e}")
            
            del active_calls[session_id]
            print(f"Cleaned up session {session_id}")
    
    return "OK"


# Route to serve audio files
@app.route("/static/<filename>")
def get_audio(filename):
    return send_from_directory('static', filename)


@app.route("/return_demo_api")
def demo_api():
    time.sleep(6)
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
    action = "schedule_demo1"
    
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