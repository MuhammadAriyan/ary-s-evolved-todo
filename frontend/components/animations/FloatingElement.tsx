'use client';

import { motion, useReducedMotion } from 'framer-motion';
import { cn } from '@/lib/utils';

export interface FloatingElementProps {
  /**
   * Animation duration in seconds
   */
  duration?: number;
  /**
   * Vertical offset in pixels
   */
  yOffset?: number;
  /**
   * Delay before animation starts in seconds
   */
  delay?: number;
  /**
   * Additional className for styling
   */
  className?: string;
  /**
   * Children elements
   */
  children: React.ReactNode;
}

export function FloatingElement({
  duration = 4,
  yOffset = 8,
  delay = 0,
  className,
  children,
}: FloatingElementProps) {
  const shouldReduceMotion = useReducedMotion();

  if (shouldReduceMotion) {
    return <div className={className}>{children}</div>;
  }

  return (
    <motion.div
      animate={{
        y: [0, -yOffset, 0],
      }}
      transition={{
        duration,
        repeat: Infinity,
        ease: 'easeInOut',
        delay,
      }}
      className={cn('will-change-transform', className)}
    >
      {children}
    </motion.div>
  );
}
