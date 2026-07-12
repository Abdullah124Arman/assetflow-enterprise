import React from 'react';
import { Outlet, Navigate, useLocation } from 'react-router-dom';
import SideNavBar from './SideNavBar';
import TopAppBar from './TopAppBar';

export default function DashboardLayout() {
  const location = useLocation();

  if (location.pathname === '/') {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background font-sans text-secondary">
      <SideNavBar />
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <TopAppBar />
        <main className="flex-1 overflow-y-auto p-6 relative">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
