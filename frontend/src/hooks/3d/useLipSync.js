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

    useFrame(() => {
        if (!vrm?.expressionManager || !audioAnalyser) return;

        if (!dataArrayRef.current) {
            dataArrayRef.current = new Uint8Array(audioAnalyser.frequencyBinCount);
        }

        // Fill dataArray with the analyser's frequency data
        const dataArray = dataArrayRef.current;
        audioAnalyser.getByteFrequencyData(dataArray);

        // Calculate average volume from frequency data
        let total = 0;
        for (let i = 0; i < dataArray.length; i++) {
            total += dataArray[i];
        }
        const average = total / dataArray.length;
        
        // Map average volume to 'aa' blend shape (range 0 to 1)
        const volume = Math.min(1, average / 40); 
        
        vrm.expressionManager.setValue('aa', volume);
    });
}
