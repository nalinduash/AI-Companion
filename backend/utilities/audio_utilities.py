import numpy as np

def bytes_to_float32(audio_bytes: bytes) -> np.ndarray:
    """Convert raw 16-bit PCM (Int16) audio bytes to Float32 NumPy array [-1.0, 1.0]."""
    int16_audio = np.frombuffer(audio_bytes, dtype=np.int16)        # Create an int16 numpy array from bytes
    float32_audio = int16_audio.astype(np.float32) / 32768.0        # Convert to float32 and normalize
    return float32_audio