from typing import List, Dict, Any
from dataclasses import dataclass, field
import json
import sys
from utils.example_company.company_about import company_data as Company_Data
from utils.example_company.example_customer import example_customer 
from utils.example_company.products_data import Products_data
from sales_agent.single_agent_graph import create_sales_graph,SalesState
from utils.groq_chat import GroqChat


class SalesConversation:
    """Manages a single sales conversation session."""
    
    def __init__(self, company_data: str = None, customer_data: Dict = None, product_info: Any = None):
        self.company_data = company_data if company_data else Company_Data
        self.customer_data = customer_data if customer_data else example_customer
        self.product_info = product_info if product_info else Products_data["products_and_services"][0]
        self.chat_history: List[Dict[str, str]] = []
        self.llm_function=GroqChat(model="llama-3.3-70b-versatile")
        self.conversation_ended = False  # Default flag set to False
        self.sales_graph = create_sales_graph(self.llm_function)

    def process_message(self, message: str) -> str:
        """Processes user input and updates the conversation."""
        self.chat_history.append({"role": "user", "content": message})
        
        state = SalesState(
            chat_history=self.chat_history,
            current_node="classifier",
            company_data=self.company_data,
            customer_data=self.customer_data,
            product_info=self.product_info,
            conversation_ended=self.conversation_ended , # Flag now included in state
            end_message={"Nothiong":"Nothing"}  # Flag now included in state

        )

        final_state = self.sales_graph.invoke(state)
        print(f"Current Node: {final_state['current_node']}")

        assistant_message = final_state["chat_history"][-1]
        self.chat_history.append(assistant_message)

        return assistant_message["content"]

    def end_conversation(self):
        """Sets the conversation_ended flag to True, triggering action node."""
        self.conversation_ended = True
        state = SalesState(
            chat_history=self.chat_history,
            current_node="classifier",
            company_data=self.company_data,
            customer_data=self.customer_data,
            product_info=self.product_info,
            conversation_ended=self.conversation_ended,
            end_message={"Nothiong":"Nothing"}  # Flag now included in state
        )

        final_state = self.sales_graph.invoke(state)
        print(f"Current Node: {final_state['current_node']}")
        return final_state["end_message"]

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Returns the chat history."""
        return self.chat_history

    def clear_conversation(self) -> None:
        """Clears the chat history."""
        self.chat_history = []
        self.conversation_ended = False  # Reset flag when clearing

    def save_conversation(self, filename: str) -> None:
        """Saves the conversation history to a file."""
        with open(filename, 'w') as f:
            json.dump(self.chat_history, f, indent=2)

    @classmethod
    def load_conversation(cls, filename: str, company_data: str, customer_data: Dict, product_info: Any) -> 'SalesConversation':
        """Loads a conversation from a file."""
        conversation = cls(company_data, customer_data, product_info)
        with open(filename, 'r') as f:
            conversation.chat_history = json.load(f)
        return conversation
