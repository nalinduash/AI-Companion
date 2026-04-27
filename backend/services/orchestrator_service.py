from services.prompt_service import PromptService
from .memory.short_term_memory_service import ShortTermMemoryService
import asyncio
from utilities.audio_utilities import bytes_to_float32, float32_to_bytes
from services.llm.llm_base import LLMBase
from .model_downloader_service import ModelDownloaderService
from .model_provider_service import ModelProvider
from .stt.stt_base import STTBase
from .tts.tts_base import TTSBase
import numpy as np
import os

class OrchestratorService:
    def __init__(self, websocket):
        self.model_downloader = ModelDownloaderService()
        self.model_downloader.ensure_models()
        
        self.model_provider = ModelProvider()
        self.prompt_service = PromptService()
        self.memory_service = ShortTermMemoryService()
        self.stt: STTBase = self.model_provider.get_stt()
        self.llm: LLMBase = self.model_provider.get_llm()
        self.tts: TTSBase = self.model_provider.get_tts()
        self.websocket = websocket
        
    async def orchestrate_audio(self, data: dict):
        try:
            audio_data = bytes_to_float32(data["bytes"])
            user_prompt = await asyncio.to_thread(self.stt.transcribe, audio_data)
            print(f"Transcribed: {user_prompt}")

            memory = self.memory_service.get_memory()
            system_prompt = self.prompt_service.build_system_prompt(memory)

            full_response = ""
            async for sentence in self.llm.stream_sentences(system_prompt, user_prompt):
                print(f"Sentence: {sentence}")
                full_response += sentence + " "
                audio = await asyncio.to_thread(self.tts.synthesize, sentence)
                audio_bytes = float32_to_bytes(audio)
                await self.websocket.send_bytes(audio_bytes)
            
            self.memory_service.add_to_memory(user_prompt, full_response.strip())
        except asyncio.CancelledError:
            print("🛑: Orchestration interrupted")