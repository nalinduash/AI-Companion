import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';

const MIN_INTERVAL = 2.0;
const MAX_INTERVAL = 6.0;
const DURATION = 0.15;

// Hook to handle automatic natural blinking for the VRM avatar
export function useBlink(vrm) {
    const nextTimeRef = useRef(getInterval());
    const startTimeRef = useRef(null);

    useFrame(({ clock }) => {
        if (!vrm?.expressionManager) return;

        const time = clock.getElapsedTime();
        const manager = vrm.expressionManager;
        
        // Handle current blink progression
        if (startTimeRef.current !== null) {
            const progress = time - startTimeRef.current;

            if (progress < DURATION) {
                const value = Math.sin((progress / DURATION) * Math.PI);
                manager.setValue('blink', value);
            } else {
                manager.setValue('blink', 0);
                startTimeRef.current = null;
                nextTimeRef.current = time + getInterval();
            }
        // Wait for next blink interval
        } else if (time >= nextTimeRef.current) {
            startTimeRef.current = time;
        }
    });
}

// Helper to get a random interval between blinks
function getInterval() {
    return MIN_INTERVAL + Math.random() * (MAX_INTERVAL - MIN_INTERVAL);
}
