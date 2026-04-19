import { useRef, useEffect } from "react";
import { int16ToFloat32 } from "@/utils/audioUtils";
import { useCoreStore } from "@/stores/useCoreStore";

// Handles audio we receive from the backend
export function useAudio() {
    const audioContextRef = useRef(null);
    const analyserRef = useRef(null);
    const nextStartTimeRef = useRef(0);
    const isStoppedRef = useRef(false);             // To handle interruptions
    const setAudioAnalyser = useCoreStore(state => state.setAudioAnalyser);

    useEffect(() => {
        return () => {
            if (audioContextRef.current) {
                audioContextRef.current.close();
            }
        };
    }, []);

    const initAudioContext = () => {
        if (!audioContextRef.current) {
            audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 24000 });
            
            // Create and configure analyser
            const analyser = audioContextRef.current.createAnalyser();
            analyser.fftSize = 256;
            analyserRef.current = analyser;
            analyser.connect(audioContextRef.current.destination);
            setAudioAnalyser(analyser);

            nextStartTimeRef.current = audioContextRef.current.currentTime;
        }
        if (audioContextRef.current.state === "suspended") {
            audioContextRef.current.resume();
        }
    };

    const addToQueue = async (audioData) => {
        if (isStoppedRef.current) return;
        initAudioContext();

        const audioArray = int16ToFloat32(audioData);

        const audioBuffer = audioContextRef.current.createBuffer(1, audioArray.length, 24000);
        audioBuffer.getChannelData(0).set(audioArray);

        const source = audioContextRef.current.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(analyserRef.current);

        // Schedule when to play the next audio
        const currentTime = audioContextRef.current.currentTime;
        if (nextStartTimeRef.current < currentTime) {
            nextStartTimeRef.current = currentTime;
        }

        source.start(nextStartTimeRef.current);
        nextStartTimeRef.current += audioBuffer.duration;
    };

    const stopPlayback = () => {
        isStoppedRef.current = true;
        if (!audioContextRef.current) return;

        audioContextRef.current.close();
        audioContextRef.current = null;
        analyserRef.current = null;
        nextStartTimeRef.current = 0;
    };

    const resumePlayback = () => {
        isStoppedRef.current = false;
    };

    return {
        addToQueue,
        initAudioContext,
        stopPlayback,
        resumePlayback
    };
}
