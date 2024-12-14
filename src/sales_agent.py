from dotenv import load_dotenv
from utils.groq_chat import GroqChat
from utils.prompts import get_persona
from company_about_summarizer import summarize_company_about
from utils.example_company.company_about import company_data
from utils.example_company.example_customer import example_customer
from utils.example_company.products_data import Products_data
from langGraph import build_sales_workflow
import os
from langgraph.graph import END

def main():
    # Load environment variables
    load_dotenv()
    
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY not found in environment variables")
        return

    # Print welcome message
    print("\n" + "="*50)
    print("Welcome to TechCare AI Sales Assistant")
    print("="*50 + "\n")

    # Initialize required data
    company_data_summarized = summarize_company_about(company_data, model_name="mixtral-8x7b-32768")

    # Initialize state
    state = {
        "messages": [],
        "customer_data": example_customer,
        "current_stage": "greeting",
        "product_info": Products_data["products_and_services"][0],
        "user_prompt": "Hello ?",
        "interaction_result": None, 
        "company_data": company_data_summarized,
        "next_step": "greeting"
    }

    # Build and run the workflow
    workflow = build_sales_workflow()
    
    try:
        agent_function = workflow.invoke(state)
        state = agent_function(state)
            
    except KeyboardInterrupt:
        print("\n\nConversation ended by user.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
    finally:
        print("\nThank you for using TechCare AI Sales Assistant!")

if __name__ == "__main__":
    main()