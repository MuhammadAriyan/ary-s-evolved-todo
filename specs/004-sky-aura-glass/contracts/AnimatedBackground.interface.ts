// Component Interface: AnimatedBackground
// Purpose: Full-screen animated gradient background with parallax effect

import { ReactNode } from 'react';

export interface AnimatedBackgroundProps {
  /**
   * Whether to enable parallax scrolling effect
   * @default true
   */
  parallax?: boolean;

  /**
   * Animation duration in seconds
   * @default 12
   */
  duration?: number;

  /**
   * Gradient color stops (4 states for smooth loop)
   * @default Sky-Aura Glass gradient states
   */
  gradientStates?: string[];

  /**
   * Z-index for background layer
   * @default -10
   */
  zIndex?: number;
}

/**
 * AnimatedBackground Component
 *
 * Renders a full-screen animated gradient background with smooth color transitions.
 * Supports parallax scrolling effect for depth perception.
 *
 * @example
 * ```tsx
 * <AnimatedBackground parallax={true} duration={12} />
 * ```
 *
 * Performance Considerations:
 * - Uses CSS transforms for GPU acceleration
 * - Respects prefers-reduced-motion
 * - Parallax disabled on low-performance devices
 */
export default function AnimatedBackground(props: AnimatedBackgroundProps): JSX.Element;
