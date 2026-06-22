import { create } from "zustand"

export const useCoreStore = create((set) => ({
    isConnected: false,
    setIsConnected: (isConnected) => set({ isConnected }),
    isListening: false,
    setIsListening: (isListening) => set({ isListening }),
    audioAnalyser: null,
    setAudioAnalyser: (audioAnalyser) => set({ audioAnalyser }),
    activeCharacter: "aria",
    setActiveCharacter: (activeCharacter) => set({ activeCharacter }),
    characters: {},
    setCharacters: (characters) => set({ characters }),
    userData: {},
    setUserData: (userData) => set({ userData }),
    currentEmotion: "neutral",
    setCurrentEmotion: (currentEmotion) => set({ currentEmotion }),
}))