from .stt_base import STTBase
import os
import numpy as np
import sherpa_onnx

# singleton pattern
class STTService(STTBase):
    def _initialize(self):
        model_dir = os.path.join(os.path.dirname(__file__), "..", "..", "models", "stt", "sherpa-onnx-nemo-parakeet_tdt_ctc_110m-en-36000-int8")
        model_dir = os.path.abspath(model_dir)
        
        self.recognizer = sherpa_onnx.OfflineRecognizer.from_nemo_ctc(
            model=os.path.join(model_dir, "model.int8.onnx"),
            tokens=os.path.join(model_dir, "tokens.txt"),
            num_threads=1,
            provider="cpu"
        )
        print("📝✅: Parakeet STT model initialized successfully.")

    def transcribe(self, audio_array: np.ndarray) -> str:
        """Process an isolated segment and return transcribed text."""
        stream = self.recognizer.create_stream()

        stream.accept_waveform(16000, audio_array)
        self.recognizer.decode_stream(stream)
        
        text = stream.result.text
        return text.strip()
