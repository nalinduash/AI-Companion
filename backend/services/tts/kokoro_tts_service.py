from .tts_base import TTSBase
import os
import numpy as np
import sherpa_onnx

# singleton pattern
class TTSService(TTSBase):
    def _initialize(self):
        model_dir = os.path.join(os.path.dirname(__file__), "..", "..", "models", "tts")
        model_dir = os.path.abspath(model_dir)

        kokoro = sherpa_onnx.OfflineTtsKokoroModelConfig(
            model=os.path.join(model_dir, "model.onnx"),
            voices=os.path.join(model_dir, "voices.bin"),
            tokens=os.path.join(model_dir, "tokens.txt"),
            data_dir=os.path.join(model_dir, "espeak-ng-data"),
            dict_dir=os.path.join(model_dir, "espeak-ng-data"),
            lang="en-us",
        )
        model_config = sherpa_onnx.OfflineTtsModelConfig(
            kokoro=kokoro,
            num_threads=4,
            provider="cuda",
            debug=False,
        )
        config = sherpa_onnx.OfflineTtsConfig(model=model_config, max_num_sentences=1)
        self.tts = sherpa_onnx.OfflineTts(config)
        print("📝✅: Kokoro TTS model initialized successfully.")

    def synthesize(self, text: str) -> np.ndarray:
        """Process text and return audio data."""
        result = self.tts.generate(text)
        return np.array(result.samples)