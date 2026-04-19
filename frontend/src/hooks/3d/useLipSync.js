import { useFrame } from '@react-three/fiber';
import { useCoreStore } from '@/stores/useCoreStore';
import { useRef } from 'react';

/**
 * Hook to synchronize the character's lip movements with audio volume.
 * It reads the frequency data from the audio analyser and updates the 'aa' blend shape.
 */
export function useLipSync(vrm) {
    const audioAnalyser = useCoreStore(state => state.audioAnalyser);
    const dataArrayRef = useRef(null);
    const smoothedVolumeRef = useRef(0);

    useFrame(() => {
        if (!vrm?.expressionManager) return;

        // Avoid character keep mouth open when interrupted
        if (!audioAnalyser) {
            vrm.expressionManager.setValue('aa', 0);
            smoothedVolumeRef.current = 0;
            return;
        }

        if (!dataArrayRef.current) {
            dataArrayRef.current = new Uint8Array(audioAnalyser.frequencyBinCount);
        }

        const dataArray = dataArrayRef.current;
        // Use Time Domain data for accurate loudness (loudness vs pitch)
        audioAnalyser.getByteTimeDomainData(dataArray);

        // Calculate RMS (Root Mean Square) volume
        let sumSquares = 0;
        for (let i = 0; i < dataArray.length; i++) {
            const amplitude = (dataArray[i] - 128) / 128;
            sumSquares += Math.pow(amplitude, 2);
        }
        const rms = Math.sqrt(sumSquares / dataArray.length);
        
        // Normalize and boost the signal for lip sync
        const targetVolume = Math.min(1, Math.pow(rms * 12.0, 1.1));
        
        // Smooth the volume transition slightly to prevent jittering
        smoothedVolumeRef.current += (targetVolume - smoothedVolumeRef.current) * 0.4;
        
        vrm.expressionManager.setValue('aa', smoothedVolumeRef.current);
    });
}
