from services.llm.llm_base import LLMBase
from .model_provider_service import ModelProvider
from .stt.stt_base import STTBase
import numpy as np
import time

class OrchestratorService:
    def __init__(self):
        self.model_provider = ModelProvider()
        self.stt: STTBase = self.model_provider.get_stt()
        self.llm: LLMBase = self.model_provider.get_llm()


    async def orchestrate(self, audio_data: np.ndarray) -> None:
        text = self.stt.transcribe(audio_data)
        print(f"Transcribed: {text}")

        # Collect the streamed response
        response_text = ""
        async for chunk in self.llm.generate(text):
            if hasattr(chunk, 'response'):
                response_text += chunk.response
            elif isinstance(chunk, str):
                response_text += chunk
        
        print(f"Response: {response_text}")