import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  // Protected routes that require authentication
  const protectedPaths = ["/todo"]
  const path = request.nextUrl.pathname

  // Check if the current path is protected
  const isProtectedPath = protectedPaths.some((protectedPath) =>
    path.startsWith(protectedPath)
  )

  if (isProtectedPath) {
    // In a real implementation, check for valid session/token
    // For now, this is a placeholder
    // TODO: Implement Better Auth session check
    return NextResponse.next()
  }

  return NextResponse.next()
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
}
