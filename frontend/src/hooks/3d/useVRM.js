import { useEffect, useRef, useState } from 'react';
import { useThree } from '@react-three/fiber';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { VRMLoaderPlugin, VRMUtils } from '@pixiv/three-vrm';

// Hook to load and manage the VRM avatar in the 3D scene
export function useVRM() {
    const { scene } = useThree();
    const vrmPath = '/characters/Aria.vrm';
    const [currentVRM, setCurrentVRM] = useState(null);
    const vrmRef = useRef(null);

    useEffect(() => {
        let isCancelled = false;

        // Load the VRM model from the specified path
        loadVRM(vrmPath).then(vrm => {
            if (isCancelled) return;
            
            setupVRM(vrm, scene);
            vrmRef.current = vrm;
            setCurrentVRM(vrm);
        }).catch(err => console.error('[👤] VRM Load error:', err));

        // Cleanup function to remove the VRM from the scene when component unmounts
        return () => {
            isCancelled = true;
            if (vrmRef.current) {
                scene.remove(vrmRef.current.scene);
                VRMUtils.deepDispose(vrmRef.current.scene);
                vrmRef.current = null;
                setCurrentVRM(null);
            }
        };
    }, [scene, vrmPath]);

    return currentVRM;
}

// Helper to initialize the GLTFLoader with VRM plugin
async function loadVRM(path) {
    return new Promise((resolve, reject) => {
        const loader = new GLTFLoader();
        loader.register((parser) => new VRMLoaderPlugin(parser));
        
        loader.load(
            path,
            (gltf) => resolve(gltf.userData.vrm),
            undefined,
            reject
        );
    });
}

// Helper to position and orient the VRM
function setupVRM(vrm, scene) {
    VRMUtils.rotateVRM0(vrm); // Ensure proper orientation
    vrm.scene.position.set(0, 0, 0);
    scene.add(vrm.scene);
}
