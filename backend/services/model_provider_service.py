from .stt.parakeet_stt_service import STTService
from .stt.stt_base import STTBase


class ModelProvider:
    def __init__(self):
        self.stt: STTBase = STTService()

    def get_stt(self) -> STTBase:
        return self.stt