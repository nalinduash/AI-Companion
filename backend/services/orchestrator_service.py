from services.llm.llm_base import LLMBase
from .model_provider_service import ModelProvider
from .stt.stt_base import STTBase
from .tts.tts_base import TTSBase
import numpy as np
import os
import wave


class OrchestratorService:
    def __init__(self):
        self.model_provider = ModelProvider()
        self.stt: STTBase = self.model_provider.get_stt()
        self.llm: LLMBase = self.model_provider.get_llm()
        self.tts: TTSBase = self.model_provider.get_tts()
        
        self.output_dir = "output/audio"
        os.makedirs(self.output_dir, exist_ok=True)


    async def orchestrate(self, audio_data: np.ndarray) -> None:
        text = self.stt.transcribe(audio_data)
        print(f"Transcribed: {text}")

        count = 0
        async for sentence in self.llm.stream_sentences(text):
            print(f"Sentence: {sentence}")
            audio = self.tts.synthesize(sentence)
            
            # Save to file
            filename = os.path.join(self.output_dir, f"sentence_{count}.wav")
            self._save_wav(filename, audio, 24000)
            print(f"Saved: {filename}")
            count += 1

    def _save_wav(self, filename: str, audio: np.ndarray, sample_rate: int):
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            # Convert float32 [-1, 1] to int16
            audio_int16 = (audio * 32767).astype(np.int16)
            wf.writeframes(audio_int16.tobytes())