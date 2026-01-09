'use client';

import { useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { renderCanvas, stopCanvas } from '@/components/ui/canvas';
import { Sparkles, ArrowRight, CheckCircle2 } from 'lucide-react';

interface HeroSectionProps {
  isAuthenticated?: boolean;
}

export function HeroSection({ isAuthenticated = false }: HeroSectionProps) {
  useEffect(() => {
    renderCanvas();
    return () => stopCanvas();
  }, []);

  return (
    <section className="relative min-h-[600px] flex items-center justify-center px-4 py-16 overflow-hidden">
      {/* Ambient Canvas Background */}
      <canvas
        id="canvas"
        className="pointer-events-none absolute inset-0 z-0"
      />

      {/* Content */}
      <div className="relative z-10 w-full max-w-2xl">
        {/* Badge */}
        <div className="flex justify-center mb-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-black/30 backdrop-blur-sm px-4 py-1.5 text-xs text-white/70">
            <Sparkles className="h-3.5 w-3.5 text-sky-400" />
            <span>Streamlined Task Management</span>
          </div>
        </div>

        <Card className="border border-white/10 bg-black/40 backdrop-blur-md shadow-2xl shadow-sky-500/10">
          <CardContent className="p-8 sm:p-12 text-center">
            <h1 className="text-3xl sm:text-5xl font-bold text-white mb-4 tracking-tight">
              Ary's Evolutioned Todo
            </h1>
            <p className="text-base sm:text-lg text-white/60 mb-8 max-w-md mx-auto leading-relaxed">
              Simple, focused task management to help you stay organized and productive
            </p>

            {/* Feature highlights */}
            <div className="flex flex-wrap justify-center gap-4 mb-8 text-sm text-white/50">
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-sky-400" />
                <span>Smart Organization</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-sky-400" />
                <span>Calendar View</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-sky-400" />
                <span>Tag System</span>
              </div>
            </div>

            {!isAuthenticated && (
              <div className="flex gap-3 justify-center">
                <Button asChild size="lg">
                  <Link href="/login" className="flex items-center gap-2">
                    Get Started
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild variant="outline" size="lg">
                  <Link href="/signup">Create Account</Link>
                </Button>
              </div>
            )}

            {isAuthenticated && (
              <Button asChild size="lg">
                <Link href="/todo" className="flex items-center gap-2">
                  Go to Tasks
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
            )}
          </CardContent>
        </Card>

        {/* Status indicator */}
        <div className="flex items-center justify-center gap-2 mt-6">
          <span className="relative flex h-2.5 w-2.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500" />
          </span>
          <span className="text-xs text-emerald-400">Available Now</span>
        </div>

        {/* Today's Focus - Demo Video */}
        <Card className="mt-8 border border-white/10 bg-black/40 backdrop-blur-md shadow-xl shadow-sky-500/5 overflow-hidden">
          <CardContent className="p-0">
            <div className="px-6 py-4 border-b border-white/10">
              <h2 className="text-sm font-medium text-white/80 flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-sky-400 animate-pulse" />
                Today's Focus
              </h2>
            </div>
            <div className="relative aspect-video bg-black/60">
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
                Your browser does not support the video tag.
              </video>
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
