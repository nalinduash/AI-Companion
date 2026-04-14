import { create } from "zustand"

export const useCoreStore = create((set) => ({
    isConnected: false,
    setIsConnected: (isConnected) => set({ isConnected }),
    isListening: false,
    setIsListening: (isListening) => set({ isListening }),
}))