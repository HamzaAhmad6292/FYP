import os
import asyncio
from typing import Optional, List, Any, Dict
from groq import AsyncGroq
from langchain_core.language_models import BaseLLM
from langchain_core.outputs import LLMResult
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from pydantic import BaseModel, Field

# Ensure API key is set as an environment variable
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise EnvironmentError("GROQ_API_KEY environment variable is not set.")

class GroqLLM(BaseLLM):
    client: Any = Field(default_factory=lambda: None)
    model: str = Field(default="mixtral-8x7b-32768")
    max_tokens: int = Field(default=500)
    temperature: float = Field(default=0.7)

    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768", max_tokens: int = 500, temperature: float = 0.7):
        super().__init__()
        self.client = AsyncGroq(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    async def _acall(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        response = await self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        return response.choices[0].message.content.strip()

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        return asyncio.run(self._acall(prompt, stop))

    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None, **kwargs: Any) -> LLMResult:
        generations = []
        for prompt in prompts:
            text = self._call(prompt, stop)
            generations.append([{"text": text}])

        return LLMResult(generations=generations)

    async def _agenerate(self, prompts: List[str], stop: Optional[List[str]] = None, **kwargs: Any) -> LLMResult:
        generations = []
        for prompt in prompts:
            text = await self._acall(prompt, stop)
            generations.append([{"text": text}])

        return LLMResult(generations=generations)

    @property
    def _llm_type(self) -> str:
        return "groq_llm"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }

# Few-shot prompt for sales techniques
FEW_SHOT_PROMPT = """
You are a professional sales assistant trained in advanced sales techniques.
Your responsibilities include engaging with customers, addressing their concerns empathetically,
and providing tailored solutions.

Here are examples of your interactions:

Example 1:
Human: I'm looking for a software to manage my team's sales pipeline.
Assistant: Great choice! A sales pipeline tool can streamline your workflow and boost efficiency.
           We recommend our solution that integrates seamlessly with your existing tools. Would you like more details?

Example 2:
Human: I'm worried about the implementation cost of this product.
Assistant: I completely understand. While the initial cost may seem high,
           the return on investment is significant due to improved team productivity and higher sales.
           Let's explore pricing options that suit your budget.

Example 3:
Human: How is your product better than others in the market?
Assistant: Excellent question! Our product stands out for its user-friendly interface, 24/7 customer support,
           and customizable features to meet your unique business needs. Can I share a case study of a client
           with similar requirements?

Now, assist the customer using these principles:
"""

# Conversation memory
memory = ConversationBufferMemory(return_messages=True)

# Main chatbot loop
async def chatbot():
    """
    Main chatbot loop for sales assistant.
    """
    llm = GroqLLM(api_key=API_KEY)
    print("Sales Assistant Chatbot Initialized. Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Chatbot session ended.")
            break

        # Prepare conversation context
        conversation_context = f"{FEW_SHOT_PROMPT}\n\nCurrent conversation history:\n{memory.chat_memory.messages}\n\nHuman: {user_input}\nAssistant:"

        # Generate response
        response = await llm._acall(conversation_context)
        print(f"Assistant: {response}")

        # Update memory
        memory.chat_memory.add_user_message(user_input)
        memory.chat_memory.add_ai_message(response)

# Run the chatbot
if __name__ == "__main__":
    asyncio.run(chatbot())
