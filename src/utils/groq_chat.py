from groq import Groq
import os
from typing import List, Dict
from dotenv import load_dotenv
import os

load_dotenv()
class GroqChat:
    def __init__(self, model="llama-3.1-8b-instant", system_prompt="You are a helpful AI assistant", 
                 temperature=0.7, max_tokens=8000):
        
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.conversation_history = []

    def chat(self, user_prompt: str, update_ctx=True, history="yes") -> str:
        if history == "no":
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"{user_prompt}"}
            ]
        else:
                messages = self.conversation_history.copy()
                messages.append({"role": "system", "content": self.system_prompt})
                messages.append({"role": "user", "content": user_prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            bot_response = response.choices[0].message.content

            if update_ctx and history == "yes":
                self.conversation_history.append({"role": "user", "content": user_prompt})
                self.conversation_history.append({"role": "assistant", "content": bot_response})

            return bot_response

        except Exception as e:
            print(f"Error in chat: {e}")
            return None

    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Return the entire conversation history."""
        return self.conversation_history

    @property
    def system_prompt(self):
        return self._system_prompt

    @system_prompt.setter
    def system_prompt(self, value):
        self._system_prompt = value
