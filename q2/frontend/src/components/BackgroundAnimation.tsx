import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';
import styled from 'styled-components';

const CanvasContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
`;

interface StarFieldProps {
  count?: number;
}

const StarField: React.FC<StarFieldProps> = ({ count = 5000 }) => {
  const ref = useRef<THREE.Points>(null);
  
  // Generate random positions for stars
  const [positions, colors] = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    
    for (let i = 0; i < count; i++) {
      // Random positions in a sphere
      const radius = Math.random() * 25 + 5;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);
      
      positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = radius * Math.cos(phi);
      
      // Random colors with blue/purple tint
      const colorIntensity = Math.random() * 0.5 + 0.5;
      colors[i * 3] = colorIntensity * 0.8; // Red
      colors[i * 3 + 1] = colorIntensity * 0.9; // Green
      colors[i * 3 + 2] = colorIntensity; // Blue
    }
    
    return [positions, colors];
  }, [count]);

  // Animate the star field
  useFrame((state) => {
    if (ref.current) {
      ref.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.1) * 0.1;
      ref.current.rotation.y = state.clock.elapsedTime * 0.05;
      ref.current.rotation.z = Math.sin(state.clock.elapsedTime * 0.05) * 0.05;
    }
  });

  return (
    <Points ref={ref} positions={positions} colors={colors}>
      <PointMaterial
        transparent
        vertexColors
        size={0.002}
        sizeAttenuation={true}
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </Points>
  );
};

interface FloatingGeometryProps {
  position: [number, number, number];
  geometry: 'sphere' | 'box' | 'octahedron';
  color: string;
  speed?: number;
}

const FloatingGeometry: React.FC<FloatingGeometryProps> = ({ 
  position, 
  geometry, 
  color, 
  speed = 1 
}) => {
  const ref = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (ref.current) {
      ref.current.rotation.x = state.clock.elapsedTime * speed * 0.2;
      ref.current.rotation.y = state.clock.elapsedTime * speed * 0.3;
      ref.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * speed) * 0.5;
    }
  });

  const GeometryComponent = () => {
    switch (geometry) {
      case 'sphere':
        return <sphereGeometry args={[0.5, 32, 32]} />;
      case 'box':
        return <boxGeometry args={[0.8, 0.8, 0.8]} />;
      case 'octahedron':
        return <octahedronGeometry args={[0.6]} />;
      default:
        return <sphereGeometry args={[0.5, 32, 32]} />;
    }
  };

  return (
    <mesh ref={ref} position={position}>
      <GeometryComponent />
      <meshStandardMaterial
        color={color}
        transparent
        opacity={0.1}
        wireframe
      />
    </mesh>
  );
};

const BackgroundAnimation: React.FC = () => {
  const geometries = useMemo(() => [
    { position: [-8, 2, -5], geometry: 'sphere', color: '#4CAF50', speed: 0.8 },
    { position: [6, -3, -8], geometry: 'box', color: '#2196F3', speed: 1.2 },
    { position: [-4, -6, -3], geometry: 'octahedron', color: '#9C27B0', speed: 0.6 },
    { position: [8, 4, -6], geometry: 'sphere', color: '#FF5722', speed: 1.0 },
    { position: [2, 8, -4], geometry: 'box', color: '#FFC107', speed: 0.9 },
    { position: [-6, 6, -7], geometry: 'octahedron', color: '#00BCD4', speed: 1.1 },
  ] as const, []);

  return (
    <CanvasContainer>
      <Canvas
        camera={{ position: [0, 0, 10], fov: 60 }}
        style={{ background: 'transparent' }}
      >
        {/* Ambient lighting */}
        <ambientLight intensity={0.2} />
        
        {/* Directional light */}
        <directionalLight
          position={[10, 10, 5]}
          intensity={0.3}
          color="#ffffff"
        />
        
        {/* Point light for dynamic lighting */}
        <pointLight
          position={[0, 0, 5]}
          intensity={0.4}
          color="#667eea"
        />
        
        {/* Star field background */}
        <StarField count={3000} />
        
        {/* Floating geometric shapes */}
        {geometries.map((geo, index) => (
          <FloatingGeometry
            key={index}
            position={geo.position}
            geometry={geo.geometry}
            color={geo.color}
            speed={geo.speed}
          />
        ))}
      </Canvas>
    </CanvasContainer>
  );
};

export default BackgroundAnimation;
