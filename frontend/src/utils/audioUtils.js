// Converts Float32Array audio data to Int16Array (16-bit PCM).
export function float32ToInt16(float32Buffer) {
    const int16Buffer = new Int16Array(float32Buffer.length);
    for (let i = 0; i < float32Buffer.length; i++) {
        const s = Math.max(-1, Math.min(1, float32Buffer[i]));
        int16Buffer[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    return int16Buffer;
}
