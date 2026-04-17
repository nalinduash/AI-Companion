from utilities.audio_utilities import bytes_to_float32, float32_to_bytes
from services.llm.llm_base import LLMBase
from .model_provider_service import ModelProvider
from .stt.stt_base import STTBase
from .tts.tts_base import TTSBase
import numpy as np


class OrchestratorService:
    def __init__(self, websocket):
        self.model_provider = ModelProvider()
        self.stt: STTBase = self.model_provider.get_stt()
        self.llm: LLMBase = self.model_provider.get_llm()
        self.tts: TTSBase = self.model_provider.get_tts()
        self.websocket = websocket
        
    async def orchestrate_audio(self, data: dict):
        audio_data = bytes_to_float32(data["bytes"])
        text = self.stt.transcribe(audio_data)
        print(f"Transcribed: {text}")

        async for sentence in self.llm.stream_sentences(text):
            print(f"Sentence: {sentence}")
            audio = self.tts.synthesize(sentence)
            audio_bytes = float32_to_bytes(audio)
            await self.websocket.send_bytes(audio_bytes)