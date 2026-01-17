/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Enable compression
  compress: true,

  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
      },
    ],
    formats: ['image/avif', 'image/webp'],
  },

  // Performance optimizations
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },

  // Optimize imports for better tree-shaking
  modularizeImports: {
    'lucide-react': {
      transform: 'lucide-react/dist/esm/icons/{{kebabCase member}}',
    },
  },

  // Experimental features for better performance
  experimental: {
    optimizePackageImports: ['framer-motion', '@tanstack/react-query', 'recharts'],
  },

  // Production optimizations (swcMinify removed - enabled by default in Next.js 15)
  poweredByHeader: false,
}

// Wrap with bundle analyzer
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

module.exports = withBundleAnalyzer(nextConfig)
