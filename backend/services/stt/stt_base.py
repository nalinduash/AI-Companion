from abc import ABC, abstractmethod
import numpy as np

# singleton pattern
class STTBase(ABC):
    _instance = None

    # create new or return existing instance
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(STTBase, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialize()
        self._initialized = True

    @abstractmethod
    def _initialize(self):
        '''
            Initialize the STT instance.
            Need to implement in child class.
        '''
        pass

    @abstractmethod
    def transcribe(self, audio_data: np.ndarray) -> str:
        '''
            Transcribe the audio data.
            Need to implement in child class.
        '''
        pass
