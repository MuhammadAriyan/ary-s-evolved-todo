'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { User, LogOut, Settings } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { authClient } from '@/lib/auth-client';
import { useRouter } from 'next/navigation';

interface UserDropdownProps {
  userName?: string;
  userEmail?: string;
}

export function UserDropdown({ userName, userEmail }: UserDropdownProps) {
  const router = useRouter();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogout = async () => {
    try {
      setIsLoggingOut(true);
      await authClient.signOut();
      router.push('/login');
    } catch (error) {
      console.error('Logout failed:', error);
      setIsLoggingOut(false);
    }
  };

  const initials = userName
    ? userName
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    : 'U';

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-cyan-400 rounded-full"
          aria-label="User menu"
        >
          <Avatar className="w-8 h-8 border-2 border-white/60 shadow-glass-sm">
            <AvatarFallback className="bg-sky-cyan-100/50 text-sky-cyan-700 text-sm font-medium">
              {initials}
            </AvatarFallback>
          </Avatar>
        </motion.button>
      </DropdownMenuTrigger>

      <DropdownMenuContent
        align="end"
        className="glass-card border-white/60 mt-2 min-w-[200px]"
      >
        {/* User Info */}
        <div className="px-3 py-2">
          <p className="text-sm font-medium text-glass">{userName || 'User'}</p>
          {userEmail && (
            <p className="text-xs text-glass-secondary truncate">{userEmail}</p>
          )}
        </div>

        <DropdownMenuSeparator className="bg-white/40" />

        {/* Settings */}
        <DropdownMenuItem
          className="cursor-pointer focus:bg-sky-cyan-50/50 text-glass-secondary"
          disabled
        >
          <Settings className="mr-2 h-4 w-4" strokeWidth={1.5} />
          <span>Settings</span>
        </DropdownMenuItem>

        <DropdownMenuSeparator className="bg-white/40" />

        {/* Logout */}
        <DropdownMenuItem
          className="cursor-pointer focus:bg-red-50/50 text-glass-secondary"
          onClick={handleLogout}
          disabled={isLoggingOut}
        >
          <LogOut className="mr-2 h-4 w-4" strokeWidth={1.5} />
          <span>{isLoggingOut ? 'Logging out...' : 'Logout'}</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
