import { useConnection } from "./useConnection"
import { useListen } from "./useListen"

export function useOrchestrator() {
    const { connect, wsRef } = useConnection()
    const { startListening, stopListening } = useListen(wsRef)

    const start = () => {
        connect()
        startListening()
    }

    const stop = () => {
        stopListening()
    }

    return {
        start,
        stop,
    }
}