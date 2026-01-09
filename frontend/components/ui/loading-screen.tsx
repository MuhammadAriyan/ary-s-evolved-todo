"use client"

import { motion } from "framer-motion"
import { Sparkles } from "lucide-react"

interface LoadingScreenProps {
  message?: string
  showBranding?: boolean
}

export function LoadingScreen({
  message = "Loading...",
  showBranding = true
}: LoadingScreenProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black">
      {/* Gradient overlay for depth */}
      <div className="absolute inset-0 bg-gradient-to-br from-black/20 via-transparent to-black/30" />

      {/* Main loading card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="relative"
      >
        {/* Glow effect behind card */}
        <motion.div
          animate={{
            opacity: [0.4, 0.7, 0.4],
            scale: [1, 1.05, 1],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute -inset-4 rounded-3xl bg-gradient-to-r from-sky-cyan-500/30 via-soft-aqua-400/20 to-sky-cyan-500/30 blur-xl"
        />

        {/* Glass card */}
        <motion.div
          animate={{ y: [0, -6, 0] }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="relative flex flex-col items-center gap-6 rounded-2xl border border-white/10 bg-black/40 px-12 py-10 backdrop-blur-xl"
        >
          {/* Animated icon */}
          <motion.div
            animate={{
              rotate: [0, 10, -10, 0],
              scale: [1, 1.1, 1],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-cyan-500 to-soft-aqua-400 shadow-lg shadow-sky-cyan-500/30"
          >
            <Sparkles className="h-8 w-8 text-white" />
          </motion.div>

          {/* Branding */}
          {showBranding && (
            <div className="text-center">
              <h1 className="bg-gradient-to-r from-white via-white to-white/80 bg-clip-text text-2xl font-semibold text-transparent">
                Ary&apos;s Evolved Todo
              </h1>
            </div>
          )}

          {/* Loading message */}
          <p className="text-sm text-white/60">{message}</p>

          {/* Animated dots */}
          <div className="flex items-center gap-2">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                animate={{
                  scale: [1, 1.3, 1],
                  opacity: [0.4, 1, 0.4],
                }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  delay: i * 0.2,
                  ease: "easeInOut",
                }}
                className="h-2 w-2 rounded-full bg-gradient-to-r from-sky-cyan-500 to-soft-aqua-400"
              />
            ))}
          </div>
        </motion.div>
      </motion.div>
    </div>
  )
}

export default LoadingScreen
