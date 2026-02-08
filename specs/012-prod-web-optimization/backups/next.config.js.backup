/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Enable standalone output for Docker
  output: 'standalone',

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

  // Exclude large ML packages from server components (they're only used client-side)
  serverExternalPackages: ['@huggingface/transformers', 'sharp', 'onnxruntime-node'],

  // Production optimizations
  poweredByHeader: false,

  // Webpack configuration to exclude large packages from serverless functions
  // Voice input uses dynamic imports and only runs in the browser, so this is safe
  webpack: (config, { isServer }) => {
    if (isServer) {
      // Mark these packages as external for serverless functions
      // They're only used client-side with dynamic imports
      config.externals = [...(config.externals || []), {
        '@huggingface/transformers': 'commonjs @huggingface/transformers',
        'sharp': 'commonjs sharp',
        'onnxruntime-node': 'commonjs onnxruntime-node',
      }]
    }

    // Ignore node-specific modules in client bundle
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        path: false,
        crypto: false,
      }
    }

    return config
  },
}

// Wrap with bundle analyzer
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

module.exports = withBundleAnalyzer(nextConfig)
