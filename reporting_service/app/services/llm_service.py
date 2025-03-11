import json
import re
from groq import AsyncGroq
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    
    async def generate(self, prompt: str) -> dict:
        try:
            response = await self.client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": f"{prompt}\nRespond ONLY with valid JSON."
                }],
                model=settings.LLM_MODEL,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            raw_content = response.choices[0].message.content
            json_content = self._extract_json(raw_content)
            return json.loads(json_content)
            
        except Exception as e:
            logger.error(f"LLM Error: {str(e)}")
            return {"error": str(e)}
    
    def _extract_json(self, text: str) -> str:
        match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
        return match.group(1) if match else text