import { useRef } from "react";
import { useCoreStore } from "@/stores/useCoreStore";

export function useConnection() {
    const wsRef = useRef(null);
    const { setIsConnected } = useCoreStore();

    const connect = () => {
        const ws = new WebSocket("ws://localhost:8000/ws/audio");
        ws.binaryType = "arraybuffer";
        wsRef.current = ws;
        
        ws.onopen = () => {
            setIsConnected(true);
        };
        
        ws.onclose = () => {
            setIsConnected(false);
        };
        
        ws.onerror = (error) => {
            console.error("🌐❌: WebSocket error:", error);
            setIsConnected(false);
        };
    };

    const disconnect = () => {
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
            setIsConnected(false);
        }
    };
    
    return {
        wsRef,
        connect,
        disconnect
    };
}