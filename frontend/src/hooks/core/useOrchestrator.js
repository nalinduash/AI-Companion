import { useConnection } from "./useConnection"
import { useListen } from "./useListen"

export function useOrchestrator() {
    const { connect } = useConnection()
    const { startListening, stopListening } = useListen()

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