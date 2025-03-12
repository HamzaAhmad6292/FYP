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
    def __init__(self, company_data: str=None, customer_data: Dict=None, product_info: Any=None):
        self.company_data = company_data if company_data else Company_Data
        self.customer_data = customer_data if customer_data else example_customer
        self.product_info = product_info if product_info else Products_data["products_and_services"][0]
        self.chat_history: List[Dict[str, str]] = []
        self.llm_function = GroqChat(model="llama-3.3-70b-versatile")
        self.sales_graph = create_sales_graph(self.llm_function)
        self.conversation_complete = False
        
    def process_message(self, message: str) -> str:
        """Process a user message and return the assistant's response."""
        # Add user message to chat history
        self.chat_history.append({"role": "user", "content": message})
        
        # Create state with current conversation context
        state = SalesState(
            chat_history=self.chat_history,
            current_node="classifier",
            company_data=self.company_data,
            customer_data=self.customer_data,
            product_info=self.product_info,
            conversation_complete=self.conversation_complete
        )
        
        # Invoke the graph with the current state
        final_state = self.sales_graph.invoke(state)
        
        # Update the chat history from the final state
        self.chat_history = final_state["chat_history"]
        
        # Return the last assistant message
        return self.chat_history[-1]["content"]
        
    def mark_conversation_complete(self) -> None:
        """External method to mark the conversation as complete."""
        self.conversation_complete = True
        
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the full conversation history."""
        return self.chat_history
    
    def clear_conversation(self) -> None:
        """Clear the conversation history and reset complete flag."""
        self.chat_history = []
        self.conversation_complete = False
        
    def save_conversation(self, filename: str) -> None:
        """Save the conversation history to a file."""
        with open(filename, 'w') as f:
            json.dump(self.chat_history, f, indent=2)
            
    @classmethod
    def load_conversation(cls, filename: str, company_data: str=None, customer_data: Dict=None, product_info: Any=None) -> 'SalesConversation':
        """Load a conversation from a file."""
        conversation = cls(company_data, customer_data, product_info)
        with open(filename, 'r') as f:
            conversation.chat_history = json.load(f)
        return conversation