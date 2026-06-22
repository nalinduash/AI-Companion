import { useVRM } from '../../hooks/3d/useVRM';
import { useAnimation } from '../../hooks/3d/useAnimation';
import { useBlink } from '../../hooks/3d/useBlink';
import { useLipSync } from '../../hooks/3d/useLipSync';
import { useEmotion } from '../../hooks/3d/useEmotion';

/**
 * Avatar component that manages the 3D character lifecycle.
 * It uses specialized hooks to load the VRM, apply animations, handle blinking, and lip sync.
 */
export default function Avatar() {
    const vrm = useVRM();
    useAnimation(vrm);
    useBlink(vrm);
    useLipSync(vrm);
    useEmotion(vrm);
}
