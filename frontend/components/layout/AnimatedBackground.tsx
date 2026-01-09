'use client';

import { motion, useReducedMotion, useScroll, useTransform } from 'framer-motion';
import { useEffect, useState } from 'react';

export function AnimatedBackground() {
  const shouldReduceMotion = useReducedMotion();
  const [mounted, setMounted] = useState(false);

  // Parallax scrolling effect - background moves at 0.5x scroll speed
  const { scrollY } = useScroll();
  const y = useTransform(scrollY, [0, 1000], [0, -500]); // 0.5x parallax

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="fixed inset-0 -z-10 bg-gradient-to-br from-misty-white via-soft-aqua to-sky-cyan-100" />
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1 }}
      style={{ y: shouldReduceMotion ? 0 : y }}
      className="fixed inset-0 -z-10 overflow-hidden"
    >
      {/* Animated Gradient Background */}
      <motion.div
        animate={
          shouldReduceMotion
            ? {}
            : {
                backgroundPosition: ['0% 50%', '50% 50%', '100% 50%', '50% 50%', '0% 50%'],
              }
        }
        transition={{
          duration: 12,
          repeat: Infinity,
          ease: 'linear',
        }}
        className="absolute inset-0 will-change-transform"
        style={{
          background: `
            linear-gradient(
              135deg,
              rgba(224, 242, 254, 0.4) 0%,
              rgba(186, 230, 253, 0.6) 25%,
              rgba(125, 211, 252, 0.3) 50%,
              rgba(186, 230, 253, 0.6) 75%,
              rgba(224, 242, 254, 0.4) 100%
            )
          `,
          backgroundSize: '400% 400%',
        }}
      />

      {/* Subtle Overlay for Depth */}
      <div
        className="absolute inset-0"
        style={{
          background: `
            radial-gradient(
              circle at 20% 30%,
              rgba(125, 211, 252, 0.15) 0%,
              transparent 50%
            ),
            radial-gradient(
              circle at 80% 70%,
              rgba(186, 230, 253, 0.15) 0%,
              transparent 50%
            )
          `,
        }}
      />
    </motion.div>
  );
}
