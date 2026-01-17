"use client"

import type React from "react"
import { useRef } from "react"
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Sparkles, ArrowRight, Zap, Shield, Clock } from "lucide-react"

interface RevolutionHeroProps {
  isAuthenticated?: boolean
}

export default function RevolutionHero({ isAuthenticated = false }: RevolutionHeroProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  const mouseX = useMotionValue(0)
  const mouseY = useMotionValue(0)

  const springConfig = { damping: 30, stiffness: 150 }
  const x = useSpring(mouseX, springConfig)
  const y = useSpring(mouseY, springConfig)

  const orbX = useTransform(x, [-300, 300], [-40, 40])
  const orbY = useTransform(y, [-300, 300], [-40, 40])
  const orbX2 = useTransform(x, [-300, 300], [30, -30])
  const orbY2 = useTransform(y, [-300, 300], [20, -20])

  const handleMouseMove = (e: React.MouseEvent) => {
    const rect = containerRef.current?.getBoundingClientRect()
    if (rect) {
      const centerX = rect.left + rect.width / 2
      const centerY = rect.top + rect.height / 2
      mouseX.set(e.clientX - centerX)
      mouseY.set(e.clientY - centerY)
    }
  }

  return (
    <div
      ref={containerRef}
      className="relative flex items-center justify-center min-h-[90vh] overflow-hidden px-6 py-20"
      onMouseMove={handleMouseMove}
    >
      {/* Animated gradient orbs */}
      <motion.div
        className="absolute top-1/4 -left-32 w-[500px] h-[500px] rounded-full bg-gradient-to-br from-aura-purple/20 via-aura-magenta/10 to-transparent blur-3xl"
        style={{ x: orbX, y: orbY }}
        animate={{
          scale: [1, 1.1, 1],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute bottom-1/4 -right-32 w-[400px] h-[400px] rounded-full bg-gradient-to-tl from-aura-gold/15 via-aura-purple/10 to-transparent blur-3xl"
        style={{ x: orbX2, y: orbY2 }}
        animate={{
          scale: [1.1, 1, 1.1],
          opacity: [0.2, 0.4, 0.2],
        }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Grid pattern overlay */}
      <div
        className="absolute inset-0 opacity-[0.02]"
        style={{
          backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
          backgroundSize: '60px 60px',
        }}
      />

      {/* Main content */}
      <div className="relative z-10 w-full max-w-6xl">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20 items-center">
          {/* Left - Text content */}
          <div className="text-center lg:text-left">
            {/* Floating badge */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="inline-flex mb-8"
            >
              <span className="relative inline-flex items-center gap-2 text-xs font-medium text-aura-purple bg-aura-purple/10 border border-aura-purple/20 rounded-full px-4 py-2 backdrop-blur-xl">
                <span className="absolute -inset-px bg-gradient-to-r from-aura-purple/20 to-aura-magenta/20 rounded-full blur-sm" />
                <Sparkles className="w-3.5 h-3.5 relative" />
                <span className="relative">Next-Gen Task Management</span>
              </span>
            </motion.div>

            {/* Main headline */}
            <motion.h1
              className="text-5xl md:text-6xl lg:text-7xl font-bold leading-[1.05] tracking-tight mb-6 font-chelsea"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.1 }}
            >
              <span className="text-white">Evolve Your </span>
              <span className="relative">
                <span className="bg-gradient-to-r from-aura-purple via-aura-magenta to-aura-gold bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient">
                  Productivity
                </span>
                <motion.span
                  className="absolute -bottom-2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-aura-purple to-transparent"
                  initial={{ scaleX: 0 }}
                  animate={{ scaleX: 1 }}
                  transition={{ duration: 0.8, delay: 0.8 }}
                />
              </span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              className="text-lg md:text-xl text-white/50 max-w-xl mx-auto lg:mx-0 mb-10 leading-relaxed"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              A beautifully crafted todo app that transforms how you organize, prioritize, and accomplish your goals.
            </motion.p>

            {/* CTA buttons */}
            <motion.div
              className="flex flex-col sm:flex-row items-center lg:items-start gap-4 mb-10"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.5 }}
            >
              {!isAuthenticated ? (
                <>
                  <Button asChild size="lg" className="relative overflow-hidden bg-gradient-to-r from-aura-purple to-aura-magenta text-white border-0 shadow-lg shadow-aura-purple/25 hover:shadow-aura-purple/40 transition-shadow group">
                    <Link href="/login" className="flex items-center gap-2">
                      <span className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
                      Get Started Free
                      <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </Link>
                  </Button>
                  <Button asChild variant="outline" size="lg" className="border-white/10 bg-white/5 text-white hover:bg-white/10 backdrop-blur-sm">
                    <Link href="/signup">Create Account</Link>
                  </Button>
                </>
              ) : (
                <Button asChild size="lg" className="relative overflow-hidden bg-gradient-to-r from-aura-purple to-aura-magenta text-white border-0 shadow-lg shadow-aura-purple/25 hover:shadow-aura-purple/40 transition-shadow group">
                  <Link href="/todo" className="flex items-center gap-2">
                    <span className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
                    Go to Tasks
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </Link>
                </Button>
              )}
            </motion.div>

            {/* Stats/trust indicators */}
            <motion.div
              className="flex flex-wrap items-center justify-center lg:justify-start gap-6 text-sm text-white/40"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.7 }}
            >
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span>Always Free</span>
              </div>
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-aura-purple" />
                <span>Secure & Private</span>
              </div>
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-aura-gold" />
                <span>Lightning Fast</span>
              </div>
            </motion.div>
          </div>

          {/* Right - Bento grid preview */}
          <motion.div
            className="relative"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <div className="grid grid-cols-2 gap-4">
              {/* Main card - Demo Video */}
              <motion.div
                className="col-span-2 rounded-2xl bg-gradient-to-br from-white/10 to-white/5 border border-white/10 backdrop-blur-xl overflow-hidden"
                whileHover={{ scale: 1.02, borderColor: "rgba(153, 41, 234, 0.3)" }}
                transition={{ duration: 0.2 }}
              >
                <div className="flex items-center gap-3 p-4 border-b border-white/10">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-aura-purple to-aura-magenta flex items-center justify-center">
                    <Clock className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="text-white font-medium">Today&apos;s Focus</p>
                    <p className="text-white/40 text-sm">See it in action</p>
                  </div>
                </div>
                <div className="relative aspect-video bg-black/40">
                  <video
                    className="w-full h-full object-cover"
                    autoPlay
                    loop
                    muted
                    playsInline
                    poster="/demo-poster.jpg"
                  >
                    <source src="/demo.mp4" type="video/mp4" />
                    <source src="/demo.webm" type="video/webm" />
                  </video>
                </div>
              </motion.div>

              {/* Stats card */}
              <motion.div
                className="p-5 rounded-2xl bg-gradient-to-br from-aura-purple/20 to-aura-purple/5 border border-aura-purple/20 backdrop-blur-xl"
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.2 }}
              >
                <p className="text-3xl font-bold text-white mb-1">94%</p>
                <p className="text-aura-purple text-sm">Completion Rate</p>
              </motion.div>

              {/* Tags card */}
              <motion.div
                className="p-5 rounded-2xl bg-gradient-to-br from-aura-magenta/20 to-aura-magenta/5 border border-aura-magenta/20 backdrop-blur-xl"
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.2 }}
              >
                <div className="flex flex-wrap gap-2">
                  <span className="px-2 py-1 text-xs rounded-full bg-aura-purple/30 text-aura-purple">Work</span>
                  <span className="px-2 py-1 text-xs rounded-full bg-aura-magenta/30 text-aura-magenta">Personal</span>
                  <span className="px-2 py-1 text-xs rounded-full bg-aura-gold/30 text-aura-gold">Health</span>
                </div>
                <p className="text-white/50 text-sm mt-2">Smart Tags</p>
              </motion.div>
            </div>

            {/* Floating decorative elements */}
            <motion.div
              className="absolute -top-4 -right-4 w-20 h-20 rounded-full bg-gradient-to-br from-aura-purple/30 to-transparent blur-xl"
              animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.8, 0.5] }}
              transition={{ duration: 4, repeat: Infinity }}
            />
            <motion.div
              className="absolute -bottom-4 -left-4 w-16 h-16 rounded-full bg-gradient-to-br from-aura-magenta/30 to-transparent blur-xl"
              animate={{ scale: [1.2, 1, 1.2], opacity: [0.5, 0.8, 0.5] }}
              transition={{ duration: 5, repeat: Infinity }}
            />
          </motion.div>
        </div>
      </div>
    </div>
  )
}

export { RevolutionHero }
