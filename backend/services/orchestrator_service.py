from services.prompt_service import PromptService
from .memory.short_term_memory_service import ShortTermMemoryService
import asyncio
from utilities.audio_utilities import bytes_to_float32, float32_to_bytes
from utilities.llm_utilities import parse_emotion_tag
from services.llm.llm_base import LLMBase
from .model_provider_service import ModelProvider
from .stt.stt_base import STTBase
from .tts.tts_base import TTSBase
import numpy as np
import os
import time
import json
import base64

class OrchestratorService:
    def __init__(self, websocket):        
        self.model_provider = ModelProvider()
        self.prompt_service = PromptService()
        self.memory_service = ShortTermMemoryService()
        self.stt: STTBase = self.model_provider.get_stt()
        self.llm: LLMBase = self.model_provider.get_llm()
        self.tts: TTSBase = self.model_provider.get_tts()
        self.websocket = websocket
        
        config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "characters.json")
        with open(config_path, "r") as f:
            self.characters_config = json.load(f)
        
    async def orchestrate_audio(self, data: dict, active_character):
        try:
            start_time = time.time()
            audio_data = bytes_to_float32(data["bytes"])
            user_prompt = await asyncio.to_thread(self.stt.transcribe, audio_data)
            transcription_end_time = time.time()
            print(f"Transcribed: {user_prompt}")

            char_config = self.characters_config.get(active_character, {})
            voice_id = char_config.get("voice_id", 0)

            memory = self.memory_service.get_memory()
            system_prompt = self.prompt_service.build_system_prompt(memory, active_character)

            full_response = ""
            first_sentence_end_time = None
            first_audio_chunk_end_time = None
            current_emotion = "neutral"

            async for raw_sentence in self.llm.stream_sentences(system_prompt, user_prompt):
                if first_sentence_end_time is None:
                    first_sentence_end_time = time.time()
                
                sentence, current_emotion = parse_emotion_tag(raw_sentence, current_emotion)
                print(f"Emotion: {current_emotion} | Sentence: {sentence} ")
                full_response += raw_sentence + " "
                audio = await asyncio.to_thread(self.tts.synthesize, sentence, voice_id)
                
                if first_audio_chunk_end_time is None:
                    first_audio_chunk_end_time = time.time()
                
                audio_bytes = float32_to_bytes(audio)
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                
                await self.websocket.send_text(json.dumps({
                    "audio": audio_b64,
                    "emotion": current_emotion
                }))
            
            self.memory_service.add_to_memory(user_prompt, full_response.strip())

            # Print timing info
            stt_time = transcription_end_time - start_time
            llm_time = (first_sentence_end_time - transcription_end_time) if first_sentence_end_time else 0
            tts_time = (first_audio_chunk_end_time - first_sentence_end_time) if first_audio_chunk_end_time and first_sentence_end_time else 0
            total_time = stt_time + llm_time + tts_time

            print(f"\n[Timing] Timing Info:")
            print(f"  - Transcription: {stt_time:.3f}s")
            print(f"  - First Sentence (LLM): {llm_time:.3f}s")
            print(f"  - First Audio Chunk (TTS): {tts_time:.3f}s")
            print(f"  - Total Latency: {total_time:.3f}s\n")

        except asyncio.CancelledError:
            print("[Orchestrator] Orchestration interrupted")