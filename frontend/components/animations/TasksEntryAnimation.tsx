'use client';

import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { GlassButton } from '@/components/ui/GlassButton';

interface TasksEntryAnimationProps {
  onComplete: () => void;
}

export function TasksEntryAnimation({ onComplete }: TasksEntryAnimationProps) {
  const [phase, setPhase] = useState<'tasks-fade' | 'content-bounce' | 'complete'>('tasks-fade');
  const [canSkip, setCanSkip] = useState(false);
  const shouldReduceMotion = useReducedMotion();

  useEffect(() => {
    // Enable skip button after 0.5s
    const skipTimer = setTimeout(() => setCanSkip(true), 500);

    // If reduced motion, skip animation entirely
    if (shouldReduceMotion) {
      onComplete();
      return;
    }

    // Phase 1: TASKS fade-in (0.5s)
    const phase1Timer = setTimeout(() => {
      setPhase('content-bounce');
    }, 500);

    // Phase 2: Content bounce-up (1s)
    const phase2Timer = setTimeout(() => {
      setPhase('complete');
      onComplete();
    }, 1500);

    return () => {
      clearTimeout(skipTimer);
      clearTimeout(phase1Timer);
      clearTimeout(phase2Timer);
    };
  }, [onComplete, shouldReduceMotion]);

  // Handle skip via button or Escape key
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && canSkip) {
        handleSkip();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [canSkip]);

  const handleSkip = () => {
    setPhase('complete');
    onComplete();
  };

  if (phase === 'complete') {
    return null;
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-br from-misty-white via-soft-aqua to-sky-cyan-100"
      >
        {/* Skip Button */}
        {canSkip && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute top-8 right-8"
          >
            <GlassButton
              onClick={handleSkip}
              variant="secondary"
              size="sm"
              className="flex items-center gap-2"
              aria-label="Skip animation (press Escape)"
            >
              <X size={16} strokeWidth={1.5} />
              <span>Skip</span>
            </GlassButton>
          </motion.div>
        )}

        {/* Animation Content */}
        <div className="relative">
          {/* Phase 1: TASKS Text Fade-in */}
          {phase === 'tasks-fade' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
              className="text-center"
            >
              <h1 className="text-8xl md:text-9xl font-light text-glass tracking-wider">
                TASKS
              </h1>
            </motion.div>
          )}

          {/* Phase 2: Content Bounce-up */}
          {phase === 'content-bounce' && (
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                duration: 1,
                ease: [0.34, 1.56, 0.64, 1], // Bounce easing
              }}
              className="text-center"
            >
              <h1 className="text-8xl md:text-9xl font-light text-glass tracking-wider mb-4">
                TASKS
              </h1>
              <p className="text-2xl text-glass-secondary">
                Your journey begins
              </p>
            </motion.div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
