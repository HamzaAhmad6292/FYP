import langgraph.graph
from typing import TypedDict, List, Optional
from utils.prompts import get_persona
from utils.chat import OllamaChat
import json

# Chat configuration (keeping the existing setup)
chat = OllamaChat(
    model='llama3.1',
    system_prompt="You are a Helpful AI",
    n_ctx=8000,
    temperature=1.2
)

# Agent State definition (keeping the existing definition)
class AgentState(TypedDict):
    conversation_history: List[str]
    customer_data: dict
    current_stage: str
    product_info: dict
    user_prompt: str
    interaction_result: Optional[str]
    company_data: str

# Existing agent functions (keeping the previously defined functions)
def greeting_agent(state: AgentState):
    response = generate_greeting_response(state)
    return {
        "conversation_history": state["conversation_history"] + [response],
        "current_stage": "pitching" if is_customer_ready(response) else "greeting"
    }

def pitching_agent(state: AgentState):
    response = generate_pitch_response(state)
    return {
        "conversation_history": state["conversation_history"] + [response],
        "current_stage": "closing" if pitch_completed(response) else "pitching"
    }

def closing_agent(state: AgentState):
    response = generate_closing_response(state)
    return {
        "conversation_history": state["conversation_history"] + [response],
        "current_stage": langgraph.graph.END if closed(response) else "pitching"
    }

def build_sales_workflow():
    workflow = langgraph.graph.StateGraph(AgentState)
    workflow.add_node("greeting", greeting_agent)
    workflow.add_node("pitching", pitching_agent)
    workflow.add_node("closing", closing_agent)
    workflow.set_entry_point("greeting")
    workflow.add_edge("greeting", "pitching")
    workflow.add_edge("greeting", "closing")
    workflow.add_edge("pitching", "closing")
    workflow.add_edge("closing", langgraph.graph.END)
    return workflow.compile()

def generate_greeting_response(state: AgentState) -> str:
    system_prompt = get_persona("general_sales_agent", company_data=state["company_data"])
    chat.system_prompt = system_prompt
    response = chat.chat(state["user_prompt"])
    return response

def is_customer_ready(conversation):
    prompt = f"""You are provided with a conversation between a sales agent and a customer. Determine if the sales agent has completed the greeting and should now proceed to pitch the product. Respond only with 'yes' or 'no' and nothing else.
 Conversation :
{conversation}
 """
    response = chat.chat(user_prompt=prompt, history="no")
    return "yes" in response.split()

def generate_pitch_response(state):
    chat.system_prompt = get_persona(
        "product_pitch_agent", 
        customer_data=json.dumps(state["customer_data"]), 
        product_service_details=json.dumps(state["product_info"])
    )
    response = chat.chat(state["user_prompt"])
    return response

def pitch_completed(conversation):
    prompt = f"""Based on the following conversation between the sales agent and the customer, does the customer want to end the conversation? Respond only with "yes" or "no."
 Conversation:
{conversation}
 """
    response = chat.chat(user_prompt=prompt, history="no")
    return "yes" in response.split()

def generate_closing_response(state):
    system_prompt = get_persona("closing_agent", company_data=state["company_data"])
    chat.system_prompt = system_prompt
    response = chat.chat(state["user_prompt"])
    return response

def closed(conversation):
    prompt = f"""Based on the following conversation between the sales agent and the customer, has the conversation ended with the sales agent bidding farewell to the customer? Respond only with 'yes' or 'no.'
 Conversation:
{conversation}
 """
    response = chat.chat(user_prompt=prompt, history="no")
    return "yes" in response.split()

# New utility functions to initialize and run the chatbot
def initialize_chatbot(company_data, product_info, customer_data=None):
    """
    Initialize the chatbot with necessary context and data.
    
    :param company_data: Dictionary containing company information
    :param product_info: Dictionary containing product/service details
    :param customer_data: Optional dictionary with customer information
    :return: Initial state for the chatbot
    """
    initial_state = {
        "conversation_history": [],
        "customer_data": customer_data or {},
        "current_stage": "greeting",
        "product_info": product_info,
        "user_prompt": "Hello, I'm interested in learning more about your product.",
        "interaction_result": None,
        "company_data": company_data
    }
    return initial_state

def run_chatbot(initial_state):
    """
    Run the chatbot workflow with the given initial state.
    
    :param initial_state: Initial state dictionary
    :return: Final conversation state
    """
    # Build the workflow
    workflow = build_sales_workflow()
    
    # Run the workflow
    final_state = workflow.invoke(initial_state)
    
    return final_state

def interactive_chat():
    """
    Interactive chat loop for the sales chatbot.
    """
    # Example initialization (you would replace these with actual data)
    company_data = {
        "name": "Example Tech Solutions",
        "industry": "Technology",
        "mission": "Providing innovative solutions"
    }
    
    product_info = {
        "name": "AI Assistant Pro",
        "description": "Advanced AI-powered productivity tool",
        "key_features": ["Intelligent task management", "Natural language processing"],
        "price": "$99/month"
    }
    
    # Initialize the chatbot
    current_state = initialize_chatbot(company_data, product_info)
    
    print("Sales Chatbot: Hello! Welcome to our service.")
    
    while True:
        # Get user input
        user_input = input("You: ")
        
        # Check for exit
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Sales Chatbot: Thank you for your time. Goodbye!")
            break
        
        # Update the state with user input
        current_state['user_prompt'] = user_input
        
        # Run the workflow
        current_state = run_chatbot(current_state)
        
        # Print the last response from the chatbot
        if current_state['conversation_history']:
            print("Sales Chatbot:", current_state['conversation_history'][-1])
        
        # Check if conversation has ended
        if current_state['current_stage'] == langgraph.graph.END:
            print("Sales Chatbot: Thank you for your time. Goodbye!")
            break

# Main execution
if __name__ == "__main__":
    interactive_chat()