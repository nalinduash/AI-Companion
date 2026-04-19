from utilities.llm_utilities import clean_text
from abc import ABC, abstractmethod
from utilities.llm_utilities import extract_sentences

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

    async def _generate(self, system_prompt: str, user_prompt: str):
        '''
            Generate a response to the given prompt.
            Make sure they stream the response and not in thinking mode.
            Need to implement in child class.
        '''
        pass

    async def stream_sentences(self, system_prompt: str, user_prompt: str):
        '''
            Stream sentences from LLM response.
        '''
        async for sentence in extract_sentences(self._generate(system_prompt, user_prompt)):
            cleaned_sentence = clean_text(sentence)
            if not cleaned_sentence:
                continue
            yield cleaned_sentence