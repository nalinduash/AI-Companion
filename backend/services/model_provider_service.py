from .llm.llm_base import LLMBase
from .stt.parakeet_stt_service import STTService
from .stt.stt_base import STTBase
from .llm.ollama_llm_service import LLMService


class ModelProvider:
    def __init__(self):
        self.stt: STTBase = STTService()
        self.llm: LLMBase = LLMService()

    def get_stt(self) -> STTBase:
        return self.stt

    def get_llm(self) -> LLMBase:
        return self.llm
