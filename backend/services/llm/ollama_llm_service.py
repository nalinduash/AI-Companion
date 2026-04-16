import ollama
from .llm_base import LLMBase

# singleton pattern
class LLMService(LLMBase):
    def _initialize(self):
        self.client = ollama.AsyncClient()
    
    async def _generate(self, prompt: str):
        response = await self.client.generate(
            model="gemma3:270m",
            prompt=prompt,
            stream=True,
            think=False
        )
        
        async for chunk in response:
            yield chunk
        
