import React from 'react';
import { Search, Bell, UserCircle } from 'lucide-react';
import { useData } from '../../providers/DataProvider';

export default function TopAppBar() {
  const { logout, currentUser } = useData();
  return (
    <header className="h-16 bg-surface border-b border-border flex items-center justify-between px-6 shrink-0">
      <div className="flex-1 flex items-center">
        <div className="relative w-96">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-tertiary" />
          <input 
            type="text" 
            placeholder="Search by tag, serial, or QR code" 
            className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded text-sm focus:outline-none focus:border-primary transition-colors"
          />
        </div>
      </div>
      <div className="flex items-center gap-4">
        <button className="p-2 text-tertiary hover:bg-background rounded-full transition-colors relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-error rounded-full"></span>
        </button>
        <div className="flex items-center gap-2 pl-4 border-l border-border">
          <UserCircle className="w-8 h-8 text-tertiary" />
          <div className="text-sm">
            <p className="font-semibold text-secondary">Current User</p>
            <p className="text-xs text-tertiary uppercase">{currentUser?.role || 'Guest'}</p>
          </div>
          <button 
            onClick={logout}
            className="ml-4 text-xs font-semibold text-primary hover:underline"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
