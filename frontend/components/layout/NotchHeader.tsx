'use client';

import { Linkedin, Github } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { UserDropdown } from './UserDropdown';

interface NotchHeaderProps {
  isAuthenticated?: boolean;
  userName?: string;
  userEmail?: string;
}

export function NotchHeader({
  isAuthenticated = false,
  userName,
  userEmail,
}: NotchHeaderProps) {
  const linkedinUrl = process.env.NEXT_PUBLIC_LINKEDIN_URL;
  const githubUrl = process.env.NEXT_PUBLIC_GITHUB_URL;

  return (
    <header className="fixed top-0 left-0 right-0 z-40 px-4 pt-4">
      <div className="mx-auto max-w-7xl">
        <nav className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-xl px-4 py-2 flex items-center justify-between shadow-lg shadow-sky-cyan-500/5">
          <span className="text-base font-semibold text-white">
            Ary&apos;s Evolved Todo
          </span>

          <div className="flex items-center gap-1">
            {linkedinUrl && (
              <Button variant="ghost" size="icon" asChild className="h-8 w-8 text-white/70 hover:text-white hover:bg-white/10">
                <a
                  href={linkedinUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="LinkedIn Profile"
                >
                  <Linkedin className="h-4 w-4" />
                </a>
              </Button>
            )}

            {githubUrl && (
              <Button variant="ghost" size="icon" asChild className="h-8 w-8 text-white/70 hover:text-white hover:bg-white/10">
                <a
                  href={githubUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="GitHub Profile"
                >
                  <Github className="h-4 w-4" />
                </a>
              </Button>
            )}

            {isAuthenticated && (
              <div className="ml-2 pl-2 border-l border-white/10">
                <UserDropdown userName={userName} userEmail={userEmail} />
              </div>
            )}
          </div>
        </nav>
      </div>
    </header>
  );
}
