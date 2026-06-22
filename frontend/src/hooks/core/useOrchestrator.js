import { useConnection } from "./useConnection"
import { useListen } from "./useListen"
import { useAudio } from "./useAudio"

export function useOrchestrator() {
    const { addToQueue, initAudioContext, stopPlayback, resumePlayback } = useAudio()
    const { connect, disconnect, wsRef } = useConnection()
    
    const handleInterrupt = () => {
        stopPlayback()
        wsRef.current?.send(JSON.stringify({ type: "interrupt" }))
    }

    // User start speaking --> handleInterrupt
    // User stop speaking  --> resumePlayback
    const { startListening, stopListening } = useListen(wsRef, handleInterrupt, resumePlayback)

    const start = () => {
        initAudioContext()
        connect()
        
        wsRef.current.onmessage = (event) => {
            if (typeof event.data === "string") {
                try {
                    const data = JSON.parse(event.data);
                    if (data.audio) {
                        const binary = window.atob(data.audio);
                        const bytes = new Uint8Array(binary.length);
                        for (let i = 0; i < binary.length; i++) {
                            bytes[i] = binary.charCodeAt(i);
                        }
                        addToQueue(bytes.buffer, data.emotion);
                    }
                } catch (e) {
                    console.error("Failed to parse websocket message:", e);
                }
            } else if (event.data instanceof ArrayBuffer) {
                addToQueue(event.data);
            }
        }
        
        startListening()
    }

    const stop = () => {
        stopListening()
        disconnect()
    }

    return {
        start,
        stop,
        handleInterrupt,
    }
}