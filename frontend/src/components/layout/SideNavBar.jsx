import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Building2, Package, ArrowRightLeft, CalendarClock, Wrench, ShieldCheck, BarChart3, Activity } from 'lucide-react';

const NAV_ITEMS = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/org-setup', label: 'Organization Setup', icon: Building2 },
  { path: '/assets', label: 'Asset Directory', icon: Package },
  { path: '/allocation', label: 'Allocation & Transfer', icon: ArrowRightLeft },
  { path: '/booking', label: 'Resource Booking', icon: CalendarClock },
  { path: '/maintenance', label: 'Maintenance', icon: Wrench },
  { path: '/audit', label: 'Asset Audit', icon: ShieldCheck },
  { path: '/reports', label: 'Reports & Analytics', icon: BarChart3 },
  { path: '/notifications', label: 'Notifications', icon: Activity },
];

export default function SideNavBar() {
  return (
    <aside className="w-64 bg-secondary text-white flex flex-col shrink-0 h-screen">
      <div className="h-16 flex items-center px-6 border-b border-white/10 shrink-0">
        <h1 className="text-xl font-bold tracking-wide text-white">AssetFlow</h1>
      </div>
      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="flex flex-col gap-1 px-3">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  className={({ isActive }) => 
                    `flex items-center gap-3 px-3 py-2 rounded transition-colors ${
                      isActive 
                        ? 'bg-primary text-white font-medium' 
                        : 'text-gray-300 hover:bg-white/10 hover:text-white'
                    }`
                  }
                >
                  <Icon className="w-5 h-5 opacity-90" />
                  <span className="text-sm">{item.label}</span>
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>
      <div className="p-4 border-t border-white/10 text-xs text-gray-400">
        <p>AssetFlow Enterprise</p>
        <p>v2.0.1</p>
      </div>
    </aside>
  );
}
