/**
 * Better Auth client for React components
 * Provides hooks for authentication and session management
 */

import { createAuthClient } from "better-auth/react"
import { jwtClient } from "better-auth/client/plugins"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
  plugins: [
    jwtClient(),
  ],
})

// Export hooks for use in components
export const { useSession, signIn, signUp, signOut } = authClient
