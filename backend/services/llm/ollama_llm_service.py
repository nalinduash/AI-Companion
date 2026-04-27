import ollama
from .llm_base import LLMBase

# singleton pattern
class LLMService(LLMBase):
    def _initialize(self):
        self.client = ollama.AsyncClient()
    
    async def _generate(self, system_prompt: str, user_prompt: str):
        response = await self.client.generate(
            model="qwen3.5:2b",
            system=system_prompt,
            prompt=user_prompt,
            stream=True,
            think=False
        )
        
        async for chunk in response:
            yield chunk
        
