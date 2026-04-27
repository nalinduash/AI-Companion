import httpx
import json
from .llm_base import LLMBase

class LLMService(LLMBase):
    def _initialize(self):
        self.url = "http://localhost:8081/v1/chat/completions"
    
    async def _generate(self, system_prompt: str, user_prompt: str):
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": True,
            "temperature": 0.5,
            "stop": ["User:", "\n\n"],  
            "chat_template_kwargs": {"enable_thinking": False} 
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", self.url, json=payload, timeout=None) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        content = line[6:].strip()
                        if content == "[DONE]":
                            break
                        data = json.loads(content)
                        # The chat endpoint nests the content inside 'choices'
                        if delta := data['choices'][0]['delta'].get('content'):
                            yield delta
