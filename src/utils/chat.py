import ollama
import os
from transformers import AutoTokenizer

class OllamaChat:
    def __init__(self, model, system_prompt="You are a helpful AI assistant", 
                 n_ctx=4096, temperature=0.7, max_tokens=1000):

        self.model = model
        self.system_prompt = system_prompt
        self.n_ctx = n_ctx
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        self.conversation_history = []
        
        # Define the file to store conversation history
        self.history_file = os.path.join(os.path.expanduser('~'), 'ollama_chat_history.txt')
        
        # Load existing conversation history from the file
        self._load_conversation()
        self.tokenizer=AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3.1-8B-Instruct",token="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")
        
    
    def _count_tokens(self, text):
        encoded_sentence = self.tokenizer.encode(text)
        token_ids = encoded_sentence[1]
        num_tokens = encoded_sentence
        return len(num_tokens) # Simplified token count; replace with your tokenizer if needed
    
    def _trim_conversation_memory(self):
        """
        Trim the conversation history to fit within the token limit.
        """
        trimmed_history = []
        current_tokens = self._count_tokens(self.system_prompt)
        
        for message in reversed(self.conversation_history):
            message_tokens = self._count_tokens(message.get('content', ''))
            
            if current_tokens + message_tokens <= self.max_tokens:
                trimmed_history.insert(0, message)
                current_tokens += message_tokens
            else:
                break
        
        self.conversation_history = trimmed_history
    
    def chat(self, user_prompt, update_ctx=True):
        """
        Handle user interaction with the model.
        
        :param user_prompt: User's input prompt
        :param update_ctx: Whether to update the conversation history
        :return: AI response
        """
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        self._trim_conversation_memory()
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_prompt})

        try:
            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={
                    'num_ctx': self.n_ctx,
                    'temperature': self.temperature
                }
            )

            bot_response = response['message']['content']

            if update_ctx:
                self.conversation_history.append({"role": "user", "content": user_prompt})
                self.conversation_history.append({"role": "assistant", "content": bot_response})
                
                self._trim_conversation_memory()
                self._save_conversation()

            return bot_response

        except Exception as e:
            print(f"Error in chat: {e}")
            return None

    def _save_conversation(self):
        """
        Save conversation history to a text file.
        """
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                for message in self.conversation_history:
                    f.write(f"{message['role']}: {message['content']}\n")
        except Exception as e:
            print(f"Error saving conversation: {e}")

    def _load_conversation(self):
        """
        Load conversation history from a text file.
        """
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                self.conversation_history = []
                for line in lines:
                    if line.strip():
                        role, content = line.split(': ', 1)
                        self.conversation_history.append({"role": role, "content": content.strip()})
                
                self._trim_conversation_memory()
        except Exception as e:
            print(f"Error loading conversation: {e}")
            self.conversation_history = []

    def clear_history(self):
        """
        Clear the conversation history and delete the history file.
        """
        self.conversation_history = []
        if os.path.exists(self.history_file):
            os.remove(self.history_file)

    def get_conversation_history(self):
        """
        Return the entire conversation history.
        
        :return: List of conversation messages
        """
        return self.conversation_history
