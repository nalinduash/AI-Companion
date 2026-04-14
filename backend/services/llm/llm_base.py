from abc import ABC, abstractmethod

# singleton pattern
class LLMBase(ABC):
    _instance = None

    # create new or return existing instance
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(LLMBase, cls).__new__(cls)
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
            Initialize the LLM instance.
            Need to implement in child class.
        '''
        pass

    async def generate(self, prompt: str):
        '''
            Generate a response to the given prompt.
            Make sure they stream the response and in not thinking mode.
            Need to implement in child class.
        '''
        pass