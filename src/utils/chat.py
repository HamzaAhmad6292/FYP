from langchain.llms import Ollama
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from typing import Optional

class OllamaChatBot:
    def __init__(
        self,
        model_name: str = "llama2",
        streaming: bool = False,
        base_url: str = "http://localhost:11434",
        system_prompt: Optional[str] = None,
        max_tokens: int = 8000
    ):
        # Initialize callbacks for streaming
        callbacks = [StreamingStdOutCallbackHandler()] if streaming else None
        callback_manager = CallbackManager(callbacks) if callbacks else None
        
        # Initialize the Ollama model
        self.llm = Ollama(
            model=model_name,
            base_url=base_url,
            callback_manager=callback_manager,
            temperature=0.7,
            system=system_prompt,
            num_ctx=max_tokens,
        )
        
        # Create a custom prompt template that includes the system prompt
        prompt_template = """
{system_prompt}

Current conversation:
{history}
Human: {input}
Assistant: Let me help you as a sales representative from TechCare AI.
"""
        
        # Initialize the prompt template
        PROMPT = PromptTemplate(
            input_variables=["history", "input", "system_prompt"],
            template=prompt_template
        )
        
        # Initialize memory with the custom prompt
        self.memory = ConversationBufferMemory()
        
        # Initialize conversation chain with the custom prompt
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=False,
            prompt=PROMPT  # Use our custom prompt template
        )
        
        self.system_prompt = system_prompt

    def chat(self, message: str) -> str:
        # Include system prompt in the conversation context
        response = self.conversation.predict(
            input=message,
            system_prompt=self.system_prompt
        )
        return response

    def clear_history(self):
        self.memory.clear()

    def get_history(self) -> str:
        return self.memory.buffer

    def update_system_prompt(self, new_system_prompt: str):
        self.system_prompt = new_system_prompt
        self.llm.system = new_system_prompt