from typing import Annotated, Any, Dict, List, Optional, Literal
from langgraph.graph import Graph, StateGraph, END
import json
from typing import TypedDict
from utils.groq_chat import GroqChat
from utils.prompts import get_persona
from utils.example_company.company_about import company_data as Company_Data
from utils.example_company.example_customer import example_customer 
from utils.example_company.products_data import Products_data
from utils.email_sender import EmailSender
import dotenv
import os
import time
import re

dotenv.load_dotenv()

class SalesState(TypedDict):
    company_data: str
    chat_history: Annotated[List[Dict[str, str]], "chat_history"] = []  
    current_node: str
    customer_data: Dict
    product_info: Any
    conversation_ended: bool  # Flag to indicate if the conversation has ended
    end_message:json ={}



def classifier(state: SalesState, llm_function: GroqChat) -> Dict[str, Any]:
    """Classifier node to determine the next conversation state."""
    
    if state["conversation_ended"]:
        return {"current_node": "action"}
    # system_prompt = """You are a sales conversation classifier.
    # Based on the chat history, determine if this is:
    # - An ongoing conversation requiring a sales pitch or an on going pitch.
    # - A conversation completed ready for closing. 
    # - If the Chat History is Empty then ouput 'greeting'
    # Return exactly one of: 'greeting', 'pitching', or 'closing'
    # Only output the required class and do not output anything else.
    # """

    if len(state["chat_history"]) == 0 or len(state["chat_history"]) == 1:
        return {"current_node": "greeting"}
    
    # user_message = state["chat_history"][-1]["content"]
    # classification = llm_function.chat(system_prompt, user_message, save_history="no").strip().lower()
    
    # # Validate and default if needed
    # if classification not in ["greeting", "pitching", "closing"]:
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

def action(state: SalesState, llm_function: GroqChat) -> Dict[str, Any]:
    """Action node to analyze sentiment, determine action, and send an email if necessary."""


    system_prompt = """You are an AI analyzing sales conversations.
    Based on the chat history, determine:

    1. SENTIMENT: Classify the overall customer sentiment as "positive", "neutral", or "negative"

    2. INTEREST: Evaluate the customer's interest level as "high", "medium", or "low"
    - "high": Customer shows clear enthusiasm or intent to purchase
    - "medium": Customer is engaged and asking questions but not ready to commit
    - "low": Customer shows minimal engagement or is just gathering basic information

    3. ACTION: Recommend the specific next step for the sales team based on the conversation context
    - This should be concrete and actionable (e.g., "Schedule follow-up call on Tuesday", "Send product brochure for Model X", etc.)
    - Action is a single line intruction to the sales team what to do after this conversation.
    - Tailor this to the customer's expressed interests and the conversation flow
    - If there is no action required then Action element can ne 'No Action'
    - If the conversation is incomplete and the call is cut then the Action should be "No Action"
    - Remember that this is after the call has ended.

    4. EMAIL ALERT: Determine if an immediate sales team notification is warranted
    - Set "send_email" to true ONLY when the customer has clearly expressed purchase intent

    Return ONLY this JSON object without additional text:
    {
    "sentiment": "positive" | "neutral" | "negative",
    "interest": "high" | "medium" | "low",
    "action": "specific next step recommendation",
    "send_email": true | false
    }
    """

    conversation = json.dumps(state["chat_history"])

    # Function to extract valid JSON from the response
    def extract_json(text):
        json_pattern = r'\{.*\}'  # Regex to find JSON-like content
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            return match.group()  # Return only the matched JSON part
        return None  # Return None if no valid JSON found

    # Retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = llm_function.chat(system_prompt, conversation, save_history="no")
            extracted_json = extract_json(result)
            if extracted_json:
                result_data = json.loads(extracted_json)
            else:
                raise json.JSONDecodeError("Invalid JSON", result, 0)
            break  # If successful, exit loop
        except (json.JSONDecodeError, TypeError):
            if attempt < max_retries - 1:
                time.sleep(1)  # Optional: Wait before retrying
                continue  # Retry
            else:
                result_data = {
                    "sentiment": "neutral",
                    "interest": "low",
                    "action": "unknown",
                    "send_email": False
                }

    # If email should be sent, construct and send the email
    if result_data.get("send_email") in ["true",True,"True"]:
        email_sender = EmailSender()
        recipient_email = "sales-team@example.com"
        subject = "Customer Interested in Purchase"
        message_text = f"""
        A customer has shown interest in purchasing {state['product_info']}.
        Sentiment: {result_data['sentiment']}
        Action Identified: {result_data['action']}
        Please follow up with the customer.
        """
        email_sender.send_email(recipient_email, message_text, subject)
    state["end_message"]= {
        "sentiment": result_data["sentiment"],
        "action": result_data["action"],
        "Conversation":state["chat_history"],
        "Email":result_data["send_email"]
    }
    return state




def create_sales_graph(llm_function:GroqChat) -> StateGraph:
    """Creates the state graph for the sales agent."""
    workflow = StateGraph(SalesState)
    
    workflow.add_node("classifier", lambda x: classifier(x, llm_function))
    workflow.add_node("greeting", lambda x: greeting(x, llm_function))
    workflow.add_node("pitching", lambda x: pitching(x, llm_function))
    workflow.add_node("closing", lambda x: closing(x, llm_function))
    workflow.add_node("action", lambda x: action(x, llm_function))

    workflow.set_entry_point("classifier")

    # Conditional transitions
    workflow.add_conditional_edges(
        "classifier",
        lambda x: x["current_node"],
        {
            "greeting": "greeting",
            "pitching": "pitching",
            "closing": "closing",
            "action": "action"  # Will go here only if conversation_ended = True
        }
    )
    
    # Define next transitions
    # workflow.add_edge("greeting", "classifier")
    # workflow.add_edge("pitching", "classifier")
    # workflow.add_edge("closing", "classifier")
    workflow.add_edge("action", END)

    return workflow.compile()

