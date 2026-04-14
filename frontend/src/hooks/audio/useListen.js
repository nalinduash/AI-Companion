import { useMicVAD } from "@ricky0123/vad-react"

export function useListen() {
    const vad = useMicVAD({
        getStream: async () => {
            return await navigator.mediaDevices.getUserMedia({      // Get mic access
                audio: {
                    channelCount: 2,  // Stereo
                    echoCancellation: true,
                    noiseSuppression: true,
                },
            })
        },

        baseAssetPath: "https://cdn.jsdelivr.net/npm/@ricky0123/vad-web@0.0.30/dist/",
        onnxWASMBasePath: "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.26.0-dev.20260410-5e55544225/dist/",
        model: "v5",
        
        onSpeechEnd: () => {
            console.log("Sent audio to server")
        },
    })

    return {
        startListening: vad.start,
        stopListening: vad.pause,
    }
}