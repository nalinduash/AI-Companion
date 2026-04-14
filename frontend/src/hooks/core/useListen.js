import { useMicVAD } from "@ricky0123/vad-react"
import { useCoreStore } from "@/stores/useCoreStore"
import { float32ToInt16 } from "@/utils/audioUtils"

export function useListen(wsRef) {
    const { setIsListening } = useCoreStore();
    const vad = useMicVAD({
        startOnLoad: false,
        getStream: async () => {
            return await navigator.mediaDevices.getUserMedia({
                audio: {
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true,
                },
            })
        },

        baseAssetPath: "https://cdn.jsdelivr.net/npm/@ricky0123/vad-web@0.0.30/dist/",
        onnxWASMBasePath: "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.26.0-dev.20260410-5e55544225/dist/",
        model: "v5",
        onSpeechEnd: (audio) => {
            const int16Buffer = float32ToInt16(audio);
            wsRef.current.send(int16Buffer.buffer);
        },
    })

    return {
        startListening: () => {
            vad.start()
            setIsListening(true)
        },
        stopListening: () => {
            vad.pause()
            setIsListening(false)
        },
    }
}