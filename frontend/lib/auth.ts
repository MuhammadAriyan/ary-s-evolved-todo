/**
 * Better Auth configuration
 * Handles email/password authentication and Google OAuth with JWT tokens
 */

import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"
import { Pool } from "pg"

export const auth = betterAuth({
  database: new Pool({
    connectionString: process.env.DATABASE_URL!,
  }),
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Set to true in production
  },
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      redirectURI: `${process.env.BETTER_AUTH_URL}/api/auth/callback/google`,
    },
  },
  session: {
    expiresIn: 60 * 60 * 24, // 24 hours
    updateAge: 60 * 60, // 1 hour
  },
  secret: process.env.BETTER_AUTH_SECRET!,
  baseURL: process.env.BETTER_AUTH_URL!,
  trustedOrigins: [process.env.BETTER_AUTH_URL!],
  plugins: [
    jwt({
      // Use the same secret as backend for JWT token generation
      secret: process.env.JWT_SECRET_KEY!,
      expiresIn: 60 * 60 * 24, // 24 hours (matches backend)
    }),
  ],
})

export type Session = typeof auth.$Infer.Session
