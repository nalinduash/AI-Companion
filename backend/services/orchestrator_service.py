from .model_provider_service import ModelProvider
from .stt.stt_base import STTBase
import numpy as np
import time

class OrchestratorService:
    def __init__(self):
        self.model_provider = ModelProvider()
        self.stt: STTBase = self.model_provider.get_stt()

    async def orchestrate(self, audio_data: np.ndarray) -> None:
        text = self.stt.transcribe(audio_data)
        print(f"Transcribed: {text}")
