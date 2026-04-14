import { useEffect, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { VRMAnimationLoaderPlugin, createVRMAnimationClip } from '@pixiv/three-vrm-animation';

const IDLE_PATH = '/animations/common/idle.vrma';

// Hook to apply idle animation to the loaded VRM
export function useAnimation(vrm) {
    const mixerRef = useRef(null);

    useEffect(() => {
        if (!vrm) return;

        mixerRef.current = new THREE.AnimationMixer(vrm.scene);
        const loader = new GLTFLoader();
        loader.register((parser) => new VRMAnimationLoaderPlugin(parser));

        loadIdle(vrm, loader, mixerRef.current);

        return () => mixerRef.current?.stopAllAction();
    }, [vrm]);

    // Update the animation mixer and VRM on every frame
    useFrame((state, delta) => {
        mixerRef.current?.update(delta);
        vrm?.update(delta);
    });
}

// Helper to load and play the idle animation
function loadIdle(vrm, loader, mixer) {
    loader.load(IDLE_PATH, (gltf) => {
        const vrmAnimation = gltf.userData.vrmAnimations?.[0];
        if (!vrmAnimation) return;

        const clip = createVRMAnimationClip(vrmAnimation, vrm);
        const action = mixer.clipAction(clip);
        action.play();
    });
}
