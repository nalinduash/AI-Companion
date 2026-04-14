import { useVRM } from '../../hooks/3d/useVRM';
import { useAnimation } from '../../hooks/3d/useAnimation';
import { useBlink } from '../../hooks/3d/useBlink';

/**
 * Avatar component that manages the 3D character lifecycle.
 * It uses specialized hooks to load the VRM, apply animations, and handle blinking.
 * It returns null because it adds objects directly to the Three.js scene via hooks.
 */
export default function Avatar() {
    const vrm = useVRM();
    useAnimation(vrm);
    useBlink(vrm);
}
