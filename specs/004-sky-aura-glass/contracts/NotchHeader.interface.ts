// Component Interface: NotchHeader
// Purpose: iPhone-style notch header with glassmorphic styling and user controls

import { ReactNode } from 'react';

export interface NotchHeaderProps {
  /**
   * LinkedIn profile URL (from environment variable)
   */
  linkedinUrl?: string;

  /**
   * GitHub profile URL (from environment variable)
   */
  githubUrl?: string;

  /**
   * Whether user is authenticated (shows UserDropdown)
   */
  isAuthenticated: boolean;

  /**
   * User email for display in dropdown
   */
  userEmail?: string;

  /**
   * Callback when logout is triggered
   */
  onLogout: () => Promise<void>;

  /**
   * Additional CSS classes
   */
  className?: string;
}

export interface NotchGeometry {
  /**
   * Notch width in pixels
   * @default 180
   */
  width: number;

  /**
   * Notch depth in pixels
   * @default 28
   */
  depth: number;
}

/**
 * NotchHeader Component
 *
 * Renders a fixed-top header with iPhone-style notch cutout containing
 * LinkedIn, GitHub, and Account icons. Displays UserDropdown when authenticated.
 *
 * @example
 * ```tsx
 * <NotchHeader
 *   linkedinUrl={process.env.NEXT_PUBLIC_LINKEDIN_URL}
 *   githubUrl={process.env.NEXT_PUBLIC_GITHUB_URL}
 *   isAuthenticated={!!session}
 *   userEmail={session?.user?.email}
 *   onLogout={handleLogout}
 * />
 * ```
 *
 * Accessibility:
 * - role="navigation"
 * - aria-label on icon buttons
 * - Keyboard navigation support
 */
export default function NotchHeader(props: NotchHeaderProps): JSX.Element;
