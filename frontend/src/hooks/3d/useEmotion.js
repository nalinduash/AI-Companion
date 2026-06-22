import { useFrame } from '@react-three/fiber';
import { useCoreStore } from '@/stores/useCoreStore';
import { useRef } from 'react';

const EMOTIONS = ['neutral', 'happy', 'relaxed', 'sad', 'angry', 'surprised'];

export function useEmotion(vrm) {
    const currentEmotion = useCoreStore(state => state.currentEmotion || "neutral");
    const currentWeightsRef = useRef({});

    useFrame((state, delta) => {
        if (!vrm?.expressionManager) return;

        const manager = vrm.expressionManager;

        EMOTIONS.forEach((emotionKey) => {
            const vrmKey = emotionKey;
            const targetWeight = emotionKey === currentEmotion ? 1.0 : 0.0;
            
            const currentWeight = currentWeightsRef.current[emotionKey] || 0;
            // Smoothly transition weights over frames
            const newWeight = currentWeight + (targetWeight - currentWeight) * 8 * delta;
            
            currentWeightsRef.current[emotionKey] = newWeight;
            manager.setValue(vrmKey, newWeight);
        });
    });
}
