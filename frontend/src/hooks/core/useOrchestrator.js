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
            if (event.data instanceof ArrayBuffer) {
                addToQueue(event.data)      // Add audio data to the audio-play queue
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
    }
}