from utils.prompts import get_persona
from utils.groq_chat import GroqChat



def summarize_company_about(company_data:str,model_name:str="llama-3.1-8b-instant") -> str:
    system_prompt = """
        You are a professional business data summarizer. Your task is to:
        - Extract key insights from company information
        - Convert complex data into clear, concise, and factual points
        - Ensure the summary is objective and easy to understand

        Rules:
        - Use bullet points for clarity
        - Do not include information not present in the original data """

    user_prompt = f"""Analyze the following company data and provide a structured summary:

    {company_data}



    Note: Do not output anything other than the summarized output.
    """



    
    chat = GroqChat(
    model=model_name if model_name is not None else None,
    system_prompt=system_prompt if system_prompt is not None else None,
    temperature=0.7,
    max_tokens=8000
    )

    
    response=chat.chat(user_prompt=user_prompt,history="no")


    return response.strip()