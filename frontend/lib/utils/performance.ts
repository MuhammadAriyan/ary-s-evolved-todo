/**
 * Performance Benchmarking Utility
 *
 * Provides CPU/GPU benchmarking to adaptively adjust animation complexity
 * based on device capabilities for optimal 60fps performance.
 */

export type DeviceComplexity = 'low' | 'medium' | 'high';

export interface PerformanceConfig {
  complexity: DeviceComplexity;
  benchmarkScore: number;
  reducedMotion: boolean;
}

export interface AnimationConfig {
  enableFloating: boolean;
  enableBreathing: boolean;
  enableParallax: boolean;
  enableStagger: boolean;
  particleCount: number;
  blurIntensity: number;
}

/**
 * Benchmark device performance by measuring animation frame rendering
 * Returns a score from 0-100 (higher is better)
 */
export function benchmarkDevice(): number {
  // Check if we're in a browser environment
  if (typeof window === 'undefined') {
    return 50; // Default medium score for SSR
  }

  // Check for cached benchmark result (valid for 24 hours)
  const cached = localStorage.getItem('device-benchmark');
  if (cached) {
    const { score, timestamp } = JSON.parse(cached);
    const age = Date.now() - timestamp;
    if (age < 24 * 60 * 60 * 1000) {
      return score;
    }
  }

  // Perform simple rendering benchmark
  const startTime = performance.now();
  let frames = 0;
  const testDuration = 100; // 100ms test

  // Create a test element with transforms
  const testElement = document.createElement('div');
  testElement.style.cssText = `
    position: fixed;
    top: -100px;
    left: -100px;
    width: 50px;
    height: 50px;
    background: rgba(125, 211, 252, 0.3);
    backdrop-filter: blur(12px);
  `;
  document.body.appendChild(testElement);

  // Animate the test element
  const animate = () => {
    if (performance.now() - startTime < testDuration) {
      frames++;
      testElement.style.transform = `translateY(${Math.sin(frames * 0.1) * 10}px)`;
      requestAnimationFrame(animate);
    } else {
      // Calculate score based on frame rate
      const fps = (frames / testDuration) * 1000;
      const score = Math.min(100, Math.round((fps / 60) * 100));

      // Cache the result
      localStorage.setItem('device-benchmark', JSON.stringify({
        score,
        timestamp: Date.now()
      }));

      // Cleanup
      document.body.removeChild(testElement);
    }
  };

  requestAnimationFrame(animate);

  // Return a default score immediately (will be updated on next render)
  return 50;
}

/**
 * Determine device complexity level based on benchmark score
 */
export function getComplexity(benchmarkScore: number): DeviceComplexity {
  if (benchmarkScore >= 75) return 'high';
  if (benchmarkScore >= 40) return 'medium';
  return 'low';
}

/**
 * Get animation configuration based on device complexity and user preferences
 */
export function getAnimationConfig(
  complexity: DeviceComplexity,
  reducedMotion: boolean = false
): AnimationConfig {
  // If user prefers reduced motion, disable all animations
  if (reducedMotion) {
    return {
      enableFloating: false,
      enableBreathing: false,
      enableParallax: false,
      enableStagger: false,
      particleCount: 0,
      blurIntensity: 0,
    };
  }

  // Configure based on device complexity
  switch (complexity) {
    case 'high':
      return {
        enableFloating: true,
        enableBreathing: true,
        enableParallax: true,
        enableStagger: true,
        particleCount: 20,
        blurIntensity: 12,
      };
    case 'medium':
      return {
        enableFloating: true,
        enableBreathing: true,
        enableParallax: false,
        enableStagger: true,
        particleCount: 10,
        blurIntensity: 8,
      };
    case 'low':
      return {
        enableFloating: false,
        enableBreathing: false,
        enableParallax: false,
        enableStagger: false,
        particleCount: 0,
        blurIntensity: 4,
      };
  }
}

/**
 * Get complete performance configuration
 */
export function getPerformanceConfig(): PerformanceConfig {
  const benchmarkScore = benchmarkDevice();
  const complexity = getComplexity(benchmarkScore);
  const reducedMotion = typeof window !== 'undefined'
    ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
    : false;

  return {
    complexity,
    benchmarkScore,
    reducedMotion,
  };
}

/**
 * Hook-friendly performance config getter
 * Use this in React components to get performance settings
 */
export function usePerformanceConfig(): PerformanceConfig {
  if (typeof window === 'undefined') {
    return {
      complexity: 'medium',
      benchmarkScore: 50,
      reducedMotion: false,
    };
  }

  return getPerformanceConfig();
}
