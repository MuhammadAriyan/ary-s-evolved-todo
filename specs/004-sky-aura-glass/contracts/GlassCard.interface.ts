// Component Interface: GlassCard
// Purpose: Reusable glassmorphic card component with optional animations

import { ReactNode, MouseEvent } from 'react';

export interface GlassCardProps {
  /**
   * Card content
   */
  children: ReactNode;

  /**
   * Enable floating animation (vertical movement)
   * @default false
   */
  floating?: boolean;

  /**
   * Enable breathing glow effect on hover
   * @default false
   */
  breathing?: boolean;

  /**
   * Glass blur intensity
   * @default 'medium' (12px)
   */
  blurIntensity?: 'light' | 'medium' | 'heavy';

  /**
   * Additional Tailwind CSS classes
   */
  className?: string;

  /**
   * Click handler
   */
  onClick?: (event: MouseEvent<HTMLDivElement>) => void;

  /**
   * ARIA role for accessibility
   */
  role?: string;

  /**
   * ARIA label for accessibility
   */
  'aria-label'?: string;
}

export interface GlassButtonProps {
  /**
   * Button content
   */
  children: ReactNode;

  /**
   * Button type
   * @default 'button'
   */
  type?: 'button' | 'submit' | 'reset';

  /**
   * Button variant
   * @default 'primary'
   */
  variant?: 'primary' | 'secondary' | 'ghost';

  /**
   * Disabled state
   * @default false
   */
  disabled?: boolean;

  /**
   * Click handler
   */
  onClick?: (event: MouseEvent<HTMLButtonElement>) => void;

  /**
   * Additional Tailwind CSS classes
   */
  className?: string;

  /**
   * ARIA label for accessibility
   */
  'aria-label'?: string;
}

/**
 * GlassCard Component
 *
 * Renders a glassmorphic card with translucent background, backdrop blur,
 * and soft bloom shadows. Supports optional floating and breathing animations.
 *
 * @example
 * ```tsx
 * <GlassCard floating breathing className="p-6">
 *   <h2>Task Title</h2>
 *   <p>Task description...</p>
 * </GlassCard>
 * ```
 *
 * Styling:
 * - backdrop-blur-md (12px)
 * - bg-white/30
 * - border-white/50
 * - shadow-bloom (multi-layer cyan/aqua/white)
 *
 * Performance:
 * - Animations disabled on low-performance devices
 * - Respects prefers-reduced-motion
 */
export function GlassCard(props: GlassCardProps): JSX.Element;

/**
 * GlassButton Component
 *
 * Renders a glassmorphic button with hover/active states and interactions.
 *
 * @example
 * ```tsx
 * <GlassButton variant="primary" onClick={handleSubmit}>
 *   Submit
 * </GlassButton>
 * ```
 *
 * Interactions:
 * - Hover: scale 1.05, brightness increase
 * - Active: scale 0.98
 * - Focus: cyan glow outline
 */
export function GlassButton(props: GlassButtonProps): JSX.Element;
