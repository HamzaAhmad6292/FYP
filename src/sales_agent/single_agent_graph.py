from typing import Annotated, Any, Dict, List, TypeVar
from langgraph.graph import Graph, StateGraph, END
from pydantic import BaseModel, Field
import json
from typing import TypedDict, List, Optional
from utils.prompts import get_persona

from utils.groq_chat import GroqChat 
# Custom state type for our sales agent
llm_function = GroqChat(model='llama-3.3-70b-versatile')

class SalesState(TypedDict):
    company_data: str
    chat_history: Annotated[List[Dict[str, str]], "chat_history"]  # Add Annotated type
    current_node: str
    customer_data: Dict
    product_info: any

def classifier(state: SalesState) -> Dict[str, Any]:
    system_prompt = """You are a sales conversation classifier.
    Based on the chat history, determine if this is:
    - A new conversation requiring a greeting
    - An ongoing conversation requiring a sales pitch
    - A conversation ready for closing
    Return exactly one of: 'greeting', 'pitching', or 'closing
    Only output the required class and donot output anything else.
    '
    """
    if state["chat_history"]==[]:
        return 'greeting'

    user_message = state["chat_history"][-1]["content"]
    classification = llm_function.chat(system_prompt, user_message)
    
    return {"current_node": classification}

def greeting(state: SalesState) -> Dict[str, Any]:
    """Greeting node for new conversations."""
    system_prompt = get_persona("general_sales_agent", company_data=state["company_data"])
    llm_function.system_prompt = system_prompt
    
    user_message = state["chat_history"][-1]["content"]
    response = llm_function.chat(user_message)
    
    new_message = {"role": "assistant", "content": response}
    return {"chat_history": [new_message]}  # Return only the new message

def pitching(state: SalesState) -> Dict[str, Any]:
    llm_function.system_prompt = get_persona(
        "product_pitch_agent",
        customer_data=json.dumps(state["customer_data"]),
        product_service_details=json.dumps(state["product_info"])
    )
    
    user_message = state["chat_history"][-1]["content"]
    response = llm_function.chat(user_message)
    
    new_message = {"role": "assistant", "content": response}
    return {"chat_history": [new_message]}  # Return only the new message

def closing(state: SalesState) -> Dict[str, Any]:
    """Closing node for finalizing sales conversations."""
    system_prompt = get_persona("closing_agent", company_data=state["company_data"])
    llm_function.system_prompt = system_prompt
    
    user_message = state["chat_history"][-1]["content"]
    response = llm_function.chat(system_prompt, user_message)
    
    new_message = {"role": "assistant", "content": response}
    return {"chat_history": [new_message]}  # Return only the new message

def create_sales_graph() -> StateGraph:
    workflow = StateGraph(SalesState)
    
    workflow.add_node("classifier", classifier)
    workflow.add_node("greeting", greeting)
    workflow.add_node("pitching", pitching)
    workflow.add_node("closing", closing)
    
    workflow.set_entry_point("classifier")
    
    # Add conditional edges based on classifier output
    workflow.add_conditional_edges(
        "classifier",
        lambda x: x["current_node"],
        {
            "greeting": "greeting",
            "pitching": "pitching",
            "closing": "closing"
        }
    )
    
    # Add edges from each node to END
    workflow.add_edge("greeting", END)
    workflow.add_edge("pitching", END)
    workflow.add_edge("closing", END)
    
    return workflow.compile()

def process_message(message: str, history: List[Dict[str, str]], company_data: str, customer_data: Dict, product_info) -> str:
    sales_graph = create_sales_graph()
    state = SalesState(
        chat_history=history + [{"role": "user", "content": message}],
        current_node="classifier",
        company_data=company_data,
        customer_data=customer_data,
        product_info=product_info
    )
    final_state = sales_graph.invoke(state)
    return final_state["chat_history"][-1]["content"]