import streamlit as st
from components.chat_interface import render_chat_interface
from sales_agent.sales_conversation import SalesConversation
def main():
    st.set_page_config(
        page_title="Sales Agent Chat Interface",
        page_icon=":microphone:",
        layout="wide"
    )
    
    # Sidebar for additional information
    with st.sidebar:
        st.header("Chat Insights")
        
        # Placeholder for chat state and metadata
    
        state_info = "Classified as 'greeting'"
        
        st.subheader("Current Session")
        st.metric("Total Messages", "Not Now Nigga")
        st.metric("Last Input Type", "Now Now Nigga")
    
    # Main application title
    st.title("Multi-Modal Chat Interface")
    
    # Initialize chat instance
    if 'chat_instance' not in st.session_state:
        st.session_state.chat_instance = SalesConversation()
    
    # Render main chat interface
    render_chat_interface(st.session_state.chat_instance)

if __name__ == "__main__":
    main()