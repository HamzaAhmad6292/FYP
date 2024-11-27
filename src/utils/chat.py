import ollama
import json
import os
import tiktoken

class OllamaChat:
    def __init__(self, model, system_prompt="You are a helpful AI assistant", 
                 n_ctx=4096, temperature=0.7, max_tokens=1000):

        self.model = model
        self.system_prompt = system_prompt
        self.n_ctx = n_ctx
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize tokenizer (using tiktoken for reliable token counting)
        self.tokenizer = tiktoken.encoding_for_model('gpt-3.5-turbo')
        
        # Initialize conversation memory
        self.conversation_history = []
        
        # Create cache directory if it doesn't exist
        self.cache_dir = os.path.join(os.path.expanduser('~'), '.ollama_chat_cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load existing conversation
        self._load_conversation()
    
    def _count_tokens(self, text):
        """
        Count tokens in a given text.
        
        :param text: Text to count tokens for
        :return: Number of tokens
        """
        return len(self.tokenizer.encode(text))
    
    def _trim_conversation_memory(self):
        """
        Trim conversation memory to stay within token limit.
        """
        # Start from the most recent messages
        trimmed_history = []
        current_tokens = 0
        
        # Add system prompt tokens
        system_tokens = self._count_tokens(self.system_prompt)
        current_tokens += system_tokens
        
        # Iterate through conversation history in reverse
        for message in reversed(self.conversation_history):
            message_tokens = self._count_tokens(message.get('content', ''))
            
            # Check if adding this message would exceed max tokens
            if current_tokens + message_tokens <= self.max_tokens:
                trimmed_history.insert(0, message)
                current_tokens += message_tokens
            else:
                break
        
        self.conversation_history = trimmed_history
    
    def chat(self, user_prompt, update_ctx=True):

        # Prepare messages for the API call
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Trim conversation memory before adding to messages
        self._trim_conversation_memory()
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_prompt})
        
        # Generate response
        try:
            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={
                    'num_ctx': self.n_ctx,
                    'temperature': self.temperature
                }
            )
            
            # Extract the response content
            bot_response = response['message']['content']
            
            # Update conversation history if requested
            if update_ctx:
                self.conversation_history.append({"role": "user", "content": user_prompt})
                self.conversation_history.append({"role": "assistant", "content": bot_response})
                
                # Ensure we stay within token limit
                self._trim_conversation_memory()
                
                # Save conversation to cache
                self._save_conversation()
            
            return bot_response
        
        except Exception as e:
            print(f"Error in chat: {e}")
            return None
    
    def _save_conversation(self):
        """
        Save conversation history to a JSON file with token tracking.
        """
        cache_file = os.path.join(self.cache_dir, f'_conversation.json')
        try:
            # Serialize only the role and content keys
            serializable_history = [
                {key: msg[key] for key in ['role', 'content'] if key in msg} 
                for msg in self.conversation_history
            ]
            
            # Create a metadata file with token information
            metadata = {
                'total_messages': len(serializable_history),
                'total_tokens': sum(self._count_tokens(msg.get('content', '')) for msg in serializable_history)
            }
            
            # Save conversation history
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_history, f, ensure_ascii=False, indent=2)
            
            # Save metadata
            with open(cache_file.replace('.json', '_metadata.json'), 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            print(f"Error saving conversation: {e}")
    
    def _load_conversation(self):
        """
        Load conversation history from a JSON file.
        """
        cache_file = os.path.join(self.cache_dir, f'_conversation.json')
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.conversation_history = json.load(f)
                
                # Trim loaded conversation to respect token limit
                self._trim_conversation_memory()
        except Exception as e:
            print(f"Error loading conversation: {e}")
            self.conversation_history = []
    
    def clear_history(self):
        """
        Clear the conversation history and related files.
        """
        self.conversation_history = []
        
        # Remove cache files
        cache_file = os.path.join(self.cache_dir, f'_conversation.json')
        metadata_file = cache_file.replace('.json', '_metadata.json')
        
        for file_path in [cache_file, metadata_file]:
            if os.path.exists(file_path):
                os.remove(file_path)