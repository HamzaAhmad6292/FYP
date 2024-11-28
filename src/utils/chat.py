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
        
        self.tokenizer = tiktoken.encoding_for_model('gpt-3.5-turbo')
        
        self.conversation_history = []
        
        self.cache_dir = os.path.join(os.path.expanduser('~'), '.ollama_chat_cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self._load_conversation()
    
    def _count_tokens(self, text):
        """
        Count tokens in a given text.
        
        :param text: Text to count tokens for
        :return: Number of tokens
        """
        return len(self.tokenizer.encode(text))
    
    def _trim_conversation_memory(self):

        trimmed_history = []
        current_tokens = 0
        
        system_tokens = self._count_tokens(self.system_prompt)
        current_tokens += system_tokens
        
        for message in reversed(self.conversation_history):
            message_tokens = self._count_tokens(message.get('content', ''))
            
            if current_tokens + message_tokens <= self.max_tokens:
                trimmed_history.insert(0, message)
                current_tokens += message_tokens
            else:
                break
        
        self.conversation_history = trimmed_history
    
    def chat(self, user_prompt, update_ctx=True):

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
        Save conversation history to a JSON file with token tracking.
        """
        cache_file = os.path.join(self.cache_dir, f'_conversation.json')
        try:
            serializable_history = [
                {key: msg[key] for key in ['role', 'content'] if key in msg} 
                for msg in self.conversation_history
            ]
            
            metadata = {
                'total_messages': len(serializable_history),
                'total_tokens': sum(self._count_tokens(msg.get('content', '')) for msg in serializable_history)
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_history, f, ensure_ascii=False, indent=2)
            
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
                
                self._trim_conversation_memory()
        except Exception as e:
            print(f"Error loading conversation: {e}")
            self.conversation_history = []
    
    def clear_history(self):
        """
        Clear the conversation history and related files.
        """
        self.conversation_history = []
        
        cache_file = os.path.join(self.cache_dir, f'_conversation.json')
        metadata_file = cache_file.replace('.json', '_metadata.json')
        
        for file_path in [cache_file, metadata_file]:
            if os.path.exists(file_path):
                os.remove(file_path)