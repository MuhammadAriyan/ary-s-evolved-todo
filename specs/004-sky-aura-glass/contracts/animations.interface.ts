// Component Interface: Animation Components
// Purpose: Reusable animation wrappers and utilities

import { ReactNode } from 'react';

export interface FloatingElementProps {
  /**
   * Content to animate
   */
  children: ReactNode;

  /**
   * Animation duration in seconds
   * @default 4
   */
  duration?: number;

  /**
   * Vertical movement offset in pixels
   * @default -12
   */
  yOffset?: number;

  /**
   * Animation delay in seconds
   * @default 0
   */
  delay?: number;

  /**
   * Additional CSS classes
   */
  className?: string;
}

export interface ScrollRevealProps {
  /**
   * Content to reveal on scroll
   */
  children: ReactNode;

  /**
   * Reveal delay in seconds
   * @default 0
   */
  delay?: number;

  /**
   * Animate only once (don't re-trigger on scroll up)
   * @default true
   */
  once?: boolean;

  /**
   * Intersection observer margin
   * @default '-100px'
   */
  margin?: string;

  /**
   * Animation variant
   * @default 'fadeInUp'
   */
  variant?: 'fadeInUp' | 'scaleIn' | 'slideInLeft' | 'slideInRight';

  /**
   * Additional CSS classes
   */
  className?: string;
}

export interface TasksEntryAnimationProps {
  /**
   * Callback when animation completes
   */
  onComplete: () => void;

  /**
   * Callback when animation is skipped
   */
  onSkip: () => void;

  /**
   * Whether animation is currently playing
   */
  isPlaying: boolean;

  /**
   * Unique key for animation (timestamp)
   */
  animationKey: string;
}

export interface EntryAnimationPhase {
  /**
   * Phase name
   */
  name: 'tasks-fade' | 'content-bounce';

  /**
   * Phase duration in seconds
   */
  duration: number;

  /**
   * Phase delay in seconds
   */
  delay: number;
}

/**
 * FloatingElement Component
 *
 * Wraps content with infinite floating animation (vertical movement).
 *
 * @example
 * ```tsx
 * <FloatingElement duration={4} yOffset={-12}>
 *   <TaskCard />
 * </FloatingElement>
 * ```
 *
 * Performance:
 * - Uses transform for GPU acceleration
 * - Disabled on low-performance devices
 * - Respects prefers-reduced-motion
 */
export function FloatingElement(props: FloatingElementProps): JSX.Element;

/**
 * ScrollReveal Component
 *
 * Reveals content with animation when it enters the viewport.
 * Uses Framer Motion's useInView hook.
 *
 * @example
 * ```tsx
 * <ScrollReveal variant="fadeInUp" delay={0.2}>
 *   <HeroSection />
 * </ScrollReveal>
 * ```
 *
 * Accessibility:
 * - Respects prefers-reduced-motion
 * - Content remains accessible even without animation
 */
export function ScrollReveal(props: ScrollRevealProps): JSX.Element;

/**
 * TasksEntryAnimation Component
 *
 * Full-screen overlay animation for todo page entry.
 * Two phases: "TASKS" text fade-in (0.5s) + content bounce-up (1s).
 *
 * @example
 * ```tsx
 * <TasksEntryAnimation
 *   isPlaying={showAnimation}
 *   animationKey={Date.now().toString()}
 *   onComplete={() => setShowAnimation(false)}
 *   onSkip={() => setShowAnimation(false)}
 * />
 * ```
 *
 * Behavior:
 * - Plays on every page visit (not just first)
 * - Skip button appears after 0.5s
 * - Can be skipped via button or Escape key
 * - Total duration: 1.5 seconds
 */
export function TasksEntryAnimation(props: TasksEntryAnimationProps): JSX.Element;

/**
 * Animation Configuration
 */
export const ANIMATION_PHASES: Record<string, EntryAnimationPhase> = {
  tasksFade: {
    name: 'tasks-fade',
    duration: 0.5,
    delay: 0,
  },
  contentBounce: {
    name: 'content-bounce',
    duration: 1,
    delay: 0.5,
  },
};
