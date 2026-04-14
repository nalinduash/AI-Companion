import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import Avatar from './Avatar';

export default function Scene() {
    return (
        <div className="fixed inset-0 -z-10 h-screen w-screen bg-slate-950">
            <Canvas
                shadows
                camera={{ position: [0, 1.45, 1.2], fov: 35 }}
                gl={{ antialias: true, alpha: true }}
            >
                <ambientLight intensity={0.8} />
                <directionalLight position={[1, 2, 3]} intensity={1.5} castShadow />
                
                <OrbitControls 
                    target={[0, 1.45, 0]} 
                    enableRotate={false} 
                    enablePan={false}
                    enableZoom={false}
                />

                <Avatar />
            </Canvas>
        </div>
    );
}
