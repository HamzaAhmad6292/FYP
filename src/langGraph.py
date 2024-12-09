from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from utils.prompts import get_persona
from utils.chat import OllamaChat
import json

chat = OllamaChat(
        model='llama3.2',  
        system_prompt="You are a Helpful AI",
        n_ctx=8000,
        temperature=1.2
    )


class AgentState(TypedDict):
    conversation_history: List[str]
    customer_data: dict
    current_stage: str
    product_info: dict
    user_prompt:str
    interaction_result: Optional[str]
    company_data:str

def greeting_agent(state: AgentState):
    response = generate_greeting_response(state)
    return {
        **state,
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
        "current_stage": END if closed(response) else "pitching"
    }

def build_sales_workflow():
    workflow = StateGraph(AgentState)
    workflow.add_node("greeting", greeting_agent)
    workflow.add_node("pitching", pitching_agent)
    workflow.add_node("closing", closing_agent)
    
    workflow.set_entry_point("greeting")
    
    workflow.add_edge("greeting", "pitching")
    workflow.add_edge("greeting", "closing")
    workflow.add_edge("pitching", "closing")
    workflow.add_edge("closing", END)

    return workflow.compile()

def generate_greeting_response(state:AgentState)->str:
    system_prompt = get_persona("general_sales_agent",company_data=state["company_data"])
    chat.system_prompt=system_prompt
    response=chat.chat(state["user_prompt"])
    return response
    

def is_customer_ready(conversation): 
    prompt=f"""You are provided with a conversation between a sales agent and a customer. Determine if the sales agent has completed the greeting and should now proceed to pitch the product. Respond only with 'yes' or 'no' and nothing else.
        Conversation :
    {conversation}
    """
    response=chat.chat(user_prompt=prompt,history="no")
    if "yes" in response.split():
        return "yes"
    else:
        return None
    



def generate_pitch_response(state):
    chat.system_prompt=get_persona("product_pitch_agent",customer_data=json.dumps(state["customer_data"]),product_service_details=json.dumps(state["product_info"])) 
    response=chat.chat(state["user_prompt"])

    return response




def pitch_completed(conversation): 
    prompt=f"""Based on the following conversation between the sales agent and the customer, does the customer want to end the conversation? Respond only with "yes" or "no."

    Conversation:
    {conversation}
    """
    response=chat.chat(user_prompt=prompt,history="no")
    if "yes" in response.split():
        return "yes"
    else:
        return None

def generate_closing_response(state):
    system_prompt = get_persona("closing_agent",company_data=state["company_data"])
    chat.system_prompt=system_prompt
    response=chat.chat(state["user_prompt"])
    return response

def closed(conversation):
    prompt=f"""Based on the following conversation between the sales agent and the customer, has the conversation ended with the sales agent bidding farewell to the customer? Respond only with 'yes' or 'no.'
    
    Conversation:
    {conversation}

    """
    response=chat.chat(user_prompt=prompt,history="no")
    if "yes" in response.split():
        return "yes"
    else:
        return None