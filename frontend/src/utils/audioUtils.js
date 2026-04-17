// Converts Float32Array audio data to Int16Array (16-bit PCM).
export function float32ToInt16(float32Buffer) {
    const int16Buffer = new Int16Array(float32Buffer.length);
    for (let i = 0; i < float32Buffer.length; i++) {
        const s = Math.max(-1, Math.min(1, float32Buffer[i]));
        int16Buffer[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    return int16Buffer;
}

// Converts Int16Array (16-bit PCM) audio data to Float32Array.
export function int16ToFloat32(audioData) {
    const int16Array = new Int16Array(audioData);
    const float32Array = new Float32Array(int16Array.length);
    for (let i = 0; i < int16Array.length; i++) {
        float32Array[i] = int16Array[i] / 32768.0;
    }
    return float32Array;
}
