'use client';

import { useEffect, useState, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { NotchHeader } from './NotchHeader';
import { SessionTimeoutModal } from './SessionTimeoutModal';
import { authClient } from '@/lib/auth-client';
import { useRouter } from 'next/navigation';

// Lazy load heavy Three.js shader background
const AnimatedShaderBackground = dynamic(
  () => import('@/components/ui/animated-shader-background'),
  { ssr: false }
);

interface PageWrapperProps {
  children: React.ReactNode;
}

const SESSION_TIMEOUT_DURATION = 2 * 60 * 60 * 1000; // 2 hours in milliseconds
const WARNING_THRESHOLD = 5 * 60 * 1000; // Show warning 5 minutes before timeout

export function PageWrapper({ children }: PageWrapperProps) {
  const router = useRouter();
  const [lastActivity, setLastActivity] = useState(Date.now());
  const [showTimeoutModal, setShowTimeoutModal] = useState(false);
  const [remainingMinutes, setRemainingMinutes] = useState(5);
  const [user, setUser] = useState<any>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Fetch user session
  useEffect(() => {
    const fetchSession = async () => {
      try {
        const session = await authClient.getSession();
        if (session?.data?.user) {
          setUser(session.data.user);
          setIsAuthenticated(true);
        }
      } catch (error) {
        console.error('Failed to fetch session:', error);
      }
    };

    fetchSession();
  }, []);

  // Update last activity on user interaction
  const updateActivity = useCallback(() => {
    setLastActivity(Date.now());
    setShowTimeoutModal(false);
  }, []);

  // Track user activity
  useEffect(() => {
    if (!isAuthenticated) return;

    const events = ['mousedown', 'keydown', 'scroll', 'touchstart'];
    events.forEach((event) => {
      window.addEventListener(event, updateActivity);
    });

    return () => {
      events.forEach((event) => {
        window.removeEventListener(event, updateActivity);
      });
    };
  }, [isAuthenticated, updateActivity]);

  // Check for session timeout
  useEffect(() => {
    if (!isAuthenticated) return;

    const interval = setInterval(() => {
      const now = Date.now();
      const timeSinceActivity = now - lastActivity;
      const timeUntilTimeout = SESSION_TIMEOUT_DURATION - timeSinceActivity;

      // Show warning modal
      if (timeUntilTimeout <= WARNING_THRESHOLD && timeUntilTimeout > 0) {
        const minutes = Math.ceil(timeUntilTimeout / 60000);
        setRemainingMinutes(minutes);
        setShowTimeoutModal(true);
      }

      // Force logout on timeout
      if (timeSinceActivity >= SESSION_TIMEOUT_DURATION) {
        handleLogout();
      }
    }, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, [isAuthenticated, lastActivity]);

  const handleExtendSession = () => {
    updateActivity();
  };

  const handleLogout = async () => {
    try {
      await authClient.signOut();
      router.push('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <>
      <AnimatedShaderBackground />
      <NotchHeader
        isAuthenticated={isAuthenticated}
        userName={user?.name}
        userEmail={user?.email}
      />
      <main className="relative min-h-screen pt-20">
        {children}
      </main>
      <SessionTimeoutModal
        isOpen={showTimeoutModal}
        onExtend={handleExtendSession}
        onLogout={handleLogout}
        remainingMinutes={remainingMinutes}
      />
    </>
  );
}
