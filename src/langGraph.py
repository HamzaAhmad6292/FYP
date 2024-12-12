from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from utils.prompts import get_persona
from utils.chat import OllamaChat
import json
import string
chat = OllamaChat(
        model='llama3.1',  
        system_prompt="You are a Helpful AI",
        n_ctx=8000,
        temperature=1.2
    )


class AgentState(TypedDict):
    messages: List[str]
    customer_data: dict
    current_stage: str
    product_info: dict
    user_prompt: str
    interaction_result: Optional[str]
    company_data: str
    next_step: str

def greeting_agent(state: AgentState):
    # Generate initial response
    response = generate_greeting_response(state)
    print("AI:", response)
    print(50*"*")
    
    # Get user's response
    user_input = input("You: ")
    print("Customer: ",user_input)
    # Update existing state
    state["messages"].append("Sales Agent: " + response)
    state["user_prompt"] = user_input
    state["messages"].append("Customer: " + user_input)
    
    # Check user's response to determine next state
    ready_response = is_customer_ready(user_input)
    print("\nClassification: Is customer ready to hear pitch?")
    print(f"Response: {ready_response}")
    print(50*"*")
    
    if ready_response == "yes":
        state["next_step"] = "pitching"
    else:
        state["next_step"] = "greeting"
        
    return state

def pitching_agent(state: AgentState):
    # Generate pitch
    response = generate_pitch_response(state)
    print("AI:", response)
    print(50*"*")
    
    # Get user's response
    user_input = input("You: ")
    print("Customer: ",user_input)
    # Update existing state
    state["messages"].append("Sales Agent: " + response)
    state["user_prompt"] = user_input
    state["messages"].append("Customer: "+user_input)
    # Check user's response to determine next state
    pitch_response = pitch_completed(user_input)
    print("\nClassification: Is pitch complete and ready for closing?")
    print(f"Response: {pitch_response}")
    print(50*"*")
    
    if pitch_response == "yes":
        state["next_step"] = "closing"
    else:
        state["next_step"] = "pitching"
        
    return state

def closing_agent(state: AgentState):
    response = generate_closing_response(state)
    print("AI:", response)
    print(50*"*")
    
    user_input = input("You: ")
    print("Customer: ",user_input)
    state["messages"].append("Sales Agent: " + response)
    state["user_prompt"] = user_input
    state["messages"].append("Customer: "+user_input)
    
    close_response = closed(user_input)
    print("\nClassification: Should the conversation end?")
    print(f"Response: {close_response}")
    print(50*"*")
    
    if close_response == "yes":
        state["next_step"] = END
    else:
        state["next_step"] = "pitching"
        
    return state

def build_sales_workflow():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("greeting", greeting_agent)
    workflow.add_node("pitching", pitching_agent)
    workflow.add_node("closing", closing_agent)
    
    workflow.set_entry_point("greeting")
    
    def router(state: AgentState) -> str:
        return state["next_step"]
    
    workflow.add_conditional_edges(
        "greeting",
        router,
        {
            "pitching": "pitching",
            "greeting": "greeting",
            "closing": "closing"
        }
    )
    
    workflow.add_conditional_edges(
        "pitching",
        router,
        {
            "pitching": "pitching",
            "closing": "closing"
        }
    )
    
    workflow.add_conditional_edges(
        "closing",
        router,
        {
            "pitching": "pitching",
            "end": END
        }
    )

    return workflow.compile()

def generate_greeting_response(state: AgentState) -> str:
    system_prompt = get_persona("general_sales_agent", company_data=state["company_data"])
    chat.system_prompt = system_prompt
    
    response = chat.chat(state["user_prompt"])
    return response
    

def is_customer_ready(conversation): 
    prompt=f"""Analyze if the customer shows interest and willingness to hear about the product. Answer only 'yes' or 'no'.
    Customer's response: {conversation}"""
    
    response=chat.chat(user_prompt=prompt,history="no")
    normalized_response=response.lower().translate(str.maketrans('', '', string.punctuation))
    print(50*"*")
    if "yes" in normalized_response.split():
        return "yes"
    else:
        return "no"
    


def generate_pitch_response(state):
    chat.system_prompt=get_persona("product_pitch_agent",customer_data=json.dumps(state["customer_data"]),product_service_details=json.dumps(state["product_info"])) 
    response=chat.chat(state["user_prompt"])
    print(response)
    print(50*"*")
    return response




def pitch_completed(conversation): 
    prompt=f"""Based on the following conversation between the sales agent and the customer, does the customer want to end the conversation? Respond only with "yes" or "no."

    Conversation:
    {conversation}
    """
    response=chat.chat(user_prompt=prompt,history="no")
    normalized_response=response.lower().translate(str.maketrans('', '', string.punctuation))
    print(50*"*")
    if "yes" in normalized_response.split():
        return "yes"
    else:
        return "no"

def generate_closing_response(state):
    system_prompt = get_persona("closing_agent",company_data=state["company_data"])
    chat.system_prompt=system_prompt
    response=chat.chat(state["user_prompt"])
    print(response)
    print(50*"*")
    return response

def closed(conversation):
    prompt=f"""Based on the following conversation between the sales agent and the customer, has the conversation ended with the sales agent bidding farewell to the customer? Respond only with 'yes' or 'no.'
    
    Conversation:
    {conversation}

    """
    response=chat.chat(user_prompt=prompt,history="no")

    normalized_response=response.lower().translate(str.maketrans('', '', string.punctuation))
    print(50*"*")
    if "yes" in normalized_response.split():
        return "yes"
    else:
        return "no"