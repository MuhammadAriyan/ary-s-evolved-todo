'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { Clock, LogOut, RefreshCw } from 'lucide-react';
import { GlassButton } from '@/components/ui/GlassButton';

interface SessionTimeoutModalProps {
  isOpen: boolean;
  onExtend: () => void;
  onLogout: () => void;
  remainingMinutes: number;
}

export function SessionTimeoutModal({
  isOpen,
  onExtend,
  onLogout,
  remainingMinutes,
}: SessionTimeoutModalProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-sky-cyan-900/20 backdrop-blur-sm z-50"
            onClick={onExtend}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
            className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-md"
          >
            <div className="glass-card p-8 mx-4">
              {/* Icon */}
              <motion.div
                animate={{ scale: [1, 1.05, 1] }}
                transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                className="flex justify-center mb-6"
              >
                <div className="w-16 h-16 rounded-full bg-sky-cyan-100/50 flex items-center justify-center">
                  <Clock className="w-8 h-8 text-sky-cyan-600" strokeWidth={1.5} />
                </div>
              </motion.div>

              {/* Title */}
              <h2 className="text-2xl font-light text-glass text-center mb-3">
                Session Timeout
              </h2>

              {/* Message */}
              <p className="text-glass-secondary text-center mb-8">
                Your session will expire in{' '}
                <span className="font-semibold text-sky-cyan-700">
                  {remainingMinutes} {remainingMinutes === 1 ? 'minute' : 'minutes'}
                </span>
                . Would you like to extend your session?
              </p>

              {/* Actions */}
              <div className="flex gap-4">
                <button
                  onClick={onLogout}
                  className="flex-1 glass-button flex items-center justify-center gap-2 hover:bg-red-50/30"
                  aria-label="Logout now"
                >
                  <LogOut size={18} strokeWidth={1.5} />
                  <span>Logout</span>
                </button>

                <button
                  onClick={onExtend}
                  className="flex-1 glass-button flex items-center justify-center gap-2 bg-sky-cyan-100/40"
                  aria-label="Extend session"
                >
                  <RefreshCw size={18} strokeWidth={1.5} />
                  <span>Extend</span>
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
