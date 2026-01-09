'use client';

import { motion, useReducedMotion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { forwardRef } from 'react';

export interface GlassCardProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'onDrag' | 'onDragStart' | 'onDragEnd'> {
  /**
   * Enable floating animation (gentle up/down motion)
   */
  floating?: boolean;
  /**
   * Enable breathing animation (subtle scale/opacity pulse)
   */
  breathing?: boolean;
  /**
   * Custom animation duration in seconds
   */
  animationDuration?: number;
  /**
   * Vertical offset for floating animation in pixels
   */
  floatOffset?: number;
  /**
   * Additional className for styling
   */
  className?: string;
  /**
   * Children elements
   */
  children?: React.ReactNode;
}

export const GlassCard = forwardRef<HTMLDivElement, GlassCardProps>(
  (
    {
      floating = false,
      breathing = false,
      animationDuration = 4,
      floatOffset = 8,
      className,
      children,
      ...props
    },
    ref
  ) => {
    const shouldReduceMotion = useReducedMotion();

    // Disable animations if user prefers reduced motion
    const enableFloating = floating && !shouldReduceMotion;
    const enableBreathing = breathing && !shouldReduceMotion;

    // Animation variants
    const floatingAnimation = enableFloating
      ? {
          y: [0, -floatOffset, 0],
        }
      : {};

    const breathingAnimation = enableBreathing
      ? {
          scale: [1, 1.02, 1],
          opacity: [0.8, 1, 0.8],
        }
      : {};

    const combinedAnimation = {
      ...floatingAnimation,
      ...breathingAnimation,
    };

    const hasAnimation = enableFloating || enableBreathing;

    if (!hasAnimation) {
      return (
        <div
          ref={ref}
          className={cn('glass-card', className)}
          {...props}
        >
          {children}
        </div>
      );
    }

    return (
      <motion.div
        ref={ref}
        animate={combinedAnimation}
        transition={{
          duration: animationDuration,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        className={cn('glass-card will-change-transform-opacity', className)}
      >
        {children}
      </motion.div>
    );
  }
);

GlassCard.displayName = 'GlassCard';
