'use client';

import { motion, useReducedMotion } from 'framer-motion';
import { Cloud } from 'lucide-react';

export function CloudBackground() {
  const shouldReduceMotion = useReducedMotion();

  const clouds = [
    { id: 1, size: 80, top: '10%', left: '10%', duration: 20, delay: 0 },
    { id: 2, size: 60, top: '20%', left: '70%', duration: 25, delay: 2 },
    { id: 3, size: 100, top: '60%', left: '15%', duration: 30, delay: 4 },
    { id: 4, size: 70, top: '70%', left: '80%', duration: 22, delay: 6 },
    { id: 5, size: 50, top: '40%', left: '50%', duration: 28, delay: 8 },
  ];

  if (shouldReduceMotion) {
    return (
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {clouds.map((cloud) => (
          <div
            key={cloud.id}
            className="absolute opacity-20"
            style={{
              top: cloud.top,
              left: cloud.left,
              width: cloud.size,
              height: cloud.size,
            }}
          >
            <Cloud className="w-full h-full text-sky-cyan-300" strokeWidth={1} />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {clouds.map((cloud) => (
        <motion.div
          key={cloud.id}
          className="absolute opacity-20"
          style={{
            top: cloud.top,
            left: cloud.left,
            width: cloud.size,
            height: cloud.size,
          }}
          animate={{
            x: [0, 30, 0],
            y: [0, -15, 0],
            scale: [1, 1.1, 1],
          }}
          transition={{
            duration: cloud.duration,
            repeat: Infinity,
            ease: 'easeInOut',
            delay: cloud.delay,
          }}
        >
          <Cloud className="w-full h-full text-sky-cyan-300" strokeWidth={1} />
        </motion.div>
      ))}
    </div>
  );
}
