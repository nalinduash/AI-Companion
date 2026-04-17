import { useRef, useEffect } from "react";
import { int16ToFloat32 } from "@/utils/audioUtils";

// Handles audio we receive from the backend
export function useAudio() {
    const audioContextRef = useRef(null);
    const nextStartTimeRef = useRef(0);

    useEffect(() => {
        return () => {
            if (audioContextRef.current) {
                audioContextRef.current.close();
            }
        };
    }, []);

    const initAudioContext = () => {
        if (!audioContextRef.current) {
            audioContextRef.current = new window.AudioContext({ sampleRate: 24000 });
            nextStartTimeRef.current = audioContextRef.current.currentTime;
        }
        if (audioContextRef.current.state === "suspended") {
            audioContextRef.current.resume();
        }
    };

    const addToQueue = async (audioData) => {
        initAudioContext();

        const audioArray = int16ToFloat32(audioData);

        const audioBuffer = audioContextRef.current.createBuffer(1, audioArray.length, 24000);
        audioBuffer.getChannelData(0).set(audioArray);

        const source = audioContextRef.current.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(audioContextRef.current.destination);

        // Schedule when to play the next audio
        const currentTime = audioContextRef.current.currentTime;
        if (nextStartTimeRef.current < currentTime) {
            nextStartTimeRef.current = currentTime;
        }

        source.start(nextStartTimeRef.current);
        nextStartTimeRef.current += audioBuffer.duration;
    };

    return {
        addToQueue,
        initAudioContext
    };
}
