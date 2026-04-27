from .llm.llm_base import LLMBase
from .stt.parakeet_stt_service import STTService
from .stt.stt_base import STTBase
from .llm.llamaCPP_llm_service import LLMService
from .tts.kokoro_tts_service import TTSService
from .tts.tts_base import TTSBase


class ModelProvider:
    def __init__(self):
        self.stt: STTBase = STTService()
        self.llm: LLMBase = LLMService()
        self.tts: TTSBase = TTSService()

    def get_stt(self) -> STTBase:
        return self.stt

    def get_llm(self) -> LLMBase:
        return self.llm

    def get_tts(self) -> TTSBase:
        return self.tts
