'use client';

import { motion, useReducedMotion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { forwardRef } from 'react';

export interface GlassButtonProps extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'onDrag' | 'onDragStart' | 'onDragEnd'> {
  /**
   * Button variant
   */
  variant?: 'default' | 'primary' | 'secondary' | 'danger';
  /**
   * Button size
   */
  size?: 'sm' | 'md' | 'lg';
  /**
   * If true, the button will take up the full width of its container
   */
  fullWidth?: boolean;
  /**
   * Additional className for styling
   */
  className?: string;
  /**
   * Children elements
   */
  children?: React.ReactNode;
}

const variantStyles = {
  default: 'glass-button',
  primary: 'glass-button bg-sky-cyan-100/40 hover:bg-sky-cyan-100/60',
  secondary: 'glass-button bg-soft-aqua/30 hover:bg-soft-aqua/50',
  danger: 'glass-button bg-red-50/30 hover:bg-red-100/50 text-red-700',
};

const sizeStyles = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
};

export const GlassButton = forwardRef<HTMLButtonElement, GlassButtonProps>(
  (
    {
      variant = 'default',
      size = 'md',
      fullWidth = false,
      className,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const shouldReduceMotion = useReducedMotion();

    const buttonClasses = cn(
      variantStyles[variant],
      sizeStyles[size],
      fullWidth && 'w-full',
      disabled && 'opacity-50 cursor-not-allowed',
      className
    );

    if (shouldReduceMotion) {
      return (
        <button
          ref={ref}
          className={buttonClasses}
          disabled={disabled}
          {...props}
        >
          {children}
        </button>
      );
    }

    return (
      <motion.button
        ref={ref}
        whileHover={disabled ? {} : { scale: 1.02, y: -2 }}
        whileTap={disabled ? {} : { scale: 0.98, y: 0 }}
        transition={{ duration: 0.2, ease: 'easeOut' }}
        className={buttonClasses}
        disabled={disabled}
      >
        {children}
      </motion.button>
    );
  }
);

GlassButton.displayName = 'GlassButton';
