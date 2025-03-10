from typing import Annotated, Any, Dict, List, TypeVar
from langgraph.graph import Graph, StateGraph, END
from pydantic import BaseModel, Field
import json
from typing import TypedDict, List, Optional
from utils.prompts import get_persona
from utils.groq_chat import GroqChat 
from supabase_client import supabase


class SalesState(TypedDict):
    company_data: str
    chat_history: Annotated[List[Dict[str, str]], "chat_history"] = []
    current_node: str
    customer_data: Dict
    product_info: any

def classifier(state: SalesState,llm_function:GroqChat) -> Dict[str, Any]:
    system_prompt = """You are a sales conversation classifier.
    Based on the chat history, determine if this is:
    - An ongoing conversation requiring a sales pitch or an on going pitch.
    - A conversation completed ready for closing. 
    - If the Chat History is Empty then ouput 'greeting'
    Return exactly one of: 'greeting', 'pitching', or 'closing
    Only output the required class and donot output anything else.
    '
    """

    if len(state["chat_history"])==1 or 0:
        print("Hamza The Great")
        return {"current_node": "greeting"}
    print("The Great Hamza")
    user_message = state["chat_history"][-1]["content"]
    classification = llm_function.chat(system_prompt, user_message,save_history="no")
    
    return {"current_node": classification}

def greeting(state: SalesState,llm_function:GroqChat) -> Dict[str, Any]:
    """Greeting node for new conversations."""
    system_prompt = get_persona("general_sales_agent", company_data=state["company_data"])
    llm_function.system_prompt = system_prompt
    
    user_message = state["chat_history"][-1]["content"]
    response = llm_function.chat(user_message)
    
    new_message = {"role": "assistant", "content": response}
    return {"chat_history": [new_message]} 

def pitching(state: SalesState,llm_function:GroqChat) -> Dict[str, Any]:
    llm_function.system_prompt = get_persona(
        "product_pitch_agent",
        customer_data=json.dumps(state["customer_data"]),
        product_service_details=json.dumps(state["product_info"])
    )
    
    user_message = state["chat_history"][-1]["content"]
    response = llm_function.chat(user_message)
    
    new_message = {"role": "assistant", "content": response}
    return {"chat_history": [new_message]} 

def closing(state: SalesState,llm_function:GroqChat) -> Dict[str, Any]:
    """Closing node for finalizing sales conversations."""
    system_prompt = get_persona("closing_agent", company_data=state["company_data"])
    llm_function.system_prompt = system_prompt
    
    user_message = state["chat_history"][-1]["content"]
    response = llm_function.chat(system_prompt, user_message)
    
    new_message = {"role": "assistant", "content": response}
    return {"chat_history": [new_message]}  

def store_conversation(state: SalesState) -> Dict[str, Any]:
    # supabase.table(TABLE_NAME).update({
    #         "processing_start_time": start_time,
    #         "task_id": task_id,
    #         "status": "processing"
    #     }).eq("Id", row_id).execute()

    # return {"chat_history": [new_message]}  
    return None

def create_sales_graph(llm_function:GroqChat) -> StateGraph:
    workflow = StateGraph(SalesState)
    
    workflow.add_node("classifier", lambda x: classifier(x, llm_function))
    workflow.add_node("greeting", lambda x: greeting(x, llm_function))
    workflow.add_node("pitching", lambda x: pitching(x, llm_function))
    workflow.add_node("closing", lambda x: closing(x, llm_function))
    workflow.add_node("store_conversation", store_conversation)
    
    workflow.set_entry_point("classifier")
    
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