from typing import Annotated, Any, Dict, List, Optional, Literal
from langgraph.graph import Graph, StateGraph, END
import json
from typing import TypedDict
from utils.groq_chat import GroqChat
from utils.prompts import get_persona
from utils.example_company.company_about import company_data as Company_Data
from utils.example_company.example_customer import example_customer 
from utils.example_company.products_data import Products_data


class SalesState(TypedDict):
    company_data: str
    chat_history: List[Dict[str, str]]
    current_node: str
    customer_data: Dict
    product_info: Any
    conversation_complete: bool


def classifier(state: SalesState, llm_function: GroqChat) -> Dict[str, Any]:
    """Classifier node to determine the next conversation state."""
    system_prompt = """You are a sales conversation classifier.
    Based on the chat history, determine if this is:
    - An ongoing conversation requiring a sales pitch or an on going pitch.
    - A conversation completed ready for closing. 
    - If the Chat History is Empty then ouput 'greeting'
    Return exactly one of: 'greeting', 'pitching', or 'closing'
    Only output the required class and do not output anything else.
    """

    if len(state["chat_history"]) == 0 or len(state["chat_history"]) == 1:
        return {"current_node": "greeting"}
    
    user_message = state["chat_history"][-1]["content"]
    classification = llm_function.chat(system_prompt, user_message, save_history="no").strip().lower()
    
    # Validate and default if needed
    if classification not in ["greeting", "pitching", "closing"]:
        classification = "pitching"  # Default to pitching if classification fails
    print("Classifier:", classification)
    
    return {"current_node": classification}


def greeting(state: SalesState, llm_function: GroqChat) -> Dict[str, Any]:
    """Greeting node for new conversations."""
    system_prompt = get_persona("general_sales_agent", company_data=state["company_data"])
    llm_function.system_prompt = system_prompt
    
    user_message = state["chat_history"][-1]["content"]
    response = llm_function.chat(user_message)
    
    new_message = {"role": "assistant", "content": response}
    new_chat_history = state["chat_history"] + [new_message]
    
    return {"chat_history": new_chat_history}


def pitching(state: SalesState, llm_function: GroqChat) -> Dict[str, Any]:
    """Pitching node for product discussions."""
    system_prompt = get_persona(
        "product_pitch_agent",
        customer_data=json.dumps(state["customer_data"]),
        product_service_details=json.dumps(state["product_info"])
    )
    llm_function.system_prompt = system_prompt
    
    user_message = state["chat_history"][-1]["content"]
    response = llm_function.chat(user_message)
    
    new_message = {"role": "assistant", "content": response}
    new_chat_history = state["chat_history"] + [new_message]
    
    return {"chat_history": new_chat_history}


def closing(state: SalesState, llm_function: GroqChat) -> Dict[str, Any]:
    """Closing node for finalizing sales conversations."""
    system_prompt = get_persona("closing_agent", company_data=state["company_data"])
    llm_function.system_prompt = system_prompt
    
    user_message = state["chat_history"][-1]["content"]
    response = llm_function.chat(system_prompt, user_message)
    
    new_message = {"role": "assistant", "content": response}
    new_chat_history = state["chat_history"] + [new_message]
    
    return {"chat_history": new_chat_history}


def should_execute_action(state: SalesState) -> str:
    """Conditional edge function to check if action node should execute."""
    if state.get("conversation_complete", False):
        return "action_node"
    else:
        return "classifier"


def action_node(state: SalesState) -> Dict[str, Any]:
    """
    Action Node that executes when the conversation is complete.
    This is a skeleton implementation that would handle various post-conversation actions.
    """
    # Example of potential actions (not implemented, just structure)
    
    # 1. Store conversation in database
    # store_conversation_in_db(state["chat_history"])
    
    # 2. Generate and save conversation summary
    # summary = generate_summary(state["chat_history"])
    # save_summary(summary, customer_id=state["customer_data"].get("id"))
    
    # 3. Extract important information
    # extracted_info = extract_information(state["chat_history"])
    # update_customer_data(state["customer_data"]["id"], extracted_info)
    
    # 4. Trigger notifications to sales team
    # notify_sales_team(state["chat_history"], state["customer_data"])
    
    return {"current_node": "action_complete"}


def create_sales_graph(llm_function: GroqChat) -> StateGraph:
    """Creates the sales conversation graph with continuous loop and action node."""
    workflow = StateGraph(SalesState)
    
    # Add nodes
    workflow.add_node("classifier", lambda x: classifier(x, llm_function))
    workflow.add_node("greeting", lambda x: greeting(x, llm_function))
    workflow.add_node("pitching", lambda x: pitching(x, llm_function))
    workflow.add_node("closing", lambda x: closing(x, llm_function))
    workflow.add_node("action_node", action_node)
    
    # Set entry point
    workflow.set_entry_point("classifier")
    
    # Add conditional edges from classifier to conversation nodes
    workflow.add_conditional_edges(
        "classifier",
        lambda x: x["current_node"],
        {
            "greeting": "greeting",
            "pitching": "pitching",
            "closing": "closing"
        }
    )
    
    # Add edges from conversation nodes back to should_execute_action
    workflow.add_conditional_edges(
        "greeting",
        should_execute_action,
        {
            "classifier": "classifier",
            "action_node": "action_node"
        }
    )
    
    workflow.add_conditional_edges(
        "pitching",
        should_execute_action,
        {
            "classifier": "classifier",
            "action_node": "action_node"
        }
    )
    
    workflow.add_conditional_edges(
        "closing",  
        should_execute_action,
        {
            "classifier": "classifier",
            "action_node": "action_node"
        }
    )
    
    # Action node leads to END
    workflow.add_edge("action_node", END)
    print("Hamza The Great")
    return workflow.compile()

