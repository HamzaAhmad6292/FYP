from utils.chat import OllamaChat
from utils.prompts import get_persona




def summarize_company_about(company_data:str) -> str:
    system_prompt = """
You are a professional business data summarizer. Your task is to:
- Extract key insights from company information
- Convert complex data into clear, concise, and factual points
- Ensure the summary is objective and easy to understand

Rules:
- Use bullet points for clarity
- Do not include information not present in the original data
"""

    user_prompt = f"""Analyze the following company data and provide a structured summary:

    {company_data}



    Note: Do not output anything other than the summarized output.
    """




    chat = OllamaChat(
        model='llama3.2',
        system_prompt=system_prompt,
        n_ctx=4096,
        temperature=0.7
        )
    
    response=chat.chat(user_prompt=user_prompt)


    return response.strip()