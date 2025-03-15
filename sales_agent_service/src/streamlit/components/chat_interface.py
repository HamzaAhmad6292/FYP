import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from sales_agent.sales_conversation import SalesConversation

def display_chat_history(chat_instance: SalesConversation):
    """
    Display the complete chat history.
    """
    chat_container = st.container()
    
    with chat_container:
        for message in chat_instance.get_conversation_history():
            role = message["role"]
            content = message["content"]
            with st.chat_message(role):
                st.write(content)

def render_text_input(chat_instance: SalesConversation):
    """
    Render text input for chat messages.
    """
    with st.form(key="message_form", clear_on_submit=True):
        user_input = st.text_input("Type your message:", key="text_input")
        submit_button = st.form_submit_button("Send")
        
        if submit_button and user_input:
            process_user_message(chat_instance, user_input, input_type="text")

def render_audio_input(chat_instance: SalesConversation):
    """
    Skeleton for audio input functionality.
    """
    with st.form(key="audio_form", clear_on_submit=True):
        audio_uploaded = st.file_uploader("Upload Audio", type=['wav', 'mp3'])
        submit_button = st.form_submit_button("Process Audio")
        
        if submit_button and audio_uploaded:
            st.warning("Audio processing not yet implemented")

def process_user_message(chat_instance: SalesConversation, message, input_type):
    """
    Process user messages from different input types.
    """
    try:
        response = chat_instance.process_message(message)
        st.rerun()
    except Exception as e:
        st.error(f"Error processing {input_type} message: {str(e)}")

def render_chat_interface(chat_instance: SalesConversation):
    """
    Main chat interface with input method selection.
    """
    st.markdown("""
        <style>
            .stApp {
                max-width: 1200px;
                margin: 0 auto;
            }
            .chat-container {
                height: 600px;
                overflow-y: auto;
                margin-bottom: 20px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        display_chat_history(chat_instance)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with st.container():
        col1, col2 = st.columns([1, 4])
        
        with col1:
            input_method = st.radio(
                "Input Method", 
                ["Text", "Audio"], 
                horizontal=True
            )
        
        with col2:
            if input_method == "Text":
                render_text_input(chat_instance)
            else:
                render_audio_input(chat_instance)
    
    # Add end conversation button
    if st.button("End Conversation"):
        end_message = chat_instance.end_conversation()
        st.success(end_message)
