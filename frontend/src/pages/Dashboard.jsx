import React from 'react';
import Card from '../components/ui/Card';
import StatusChip from '../components/ui/StatusChip';
import { useData } from '../providers/DataProvider';
import { Package, Wrench, ShieldCheck, Activity } from 'lucide-react';

export default function Dashboard() {
  const { assets, maintenance, initialAudit } = useData();

  const totalAssets = assets.length;
  const activeMaintenance = maintenance.pending.length + maintenance.approved.length + maintenance.assigned.length + maintenance.inProgress.length;
  const activeAudits = initialAudit.length;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold text-secondary">Dashboard</h1>
        <p className="text-tertiary">Welcome back, here is your system overview.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6 flex items-center gap-4 border-t-4 border-t-primary">
          <div className="p-3 bg-primary/10 text-primary rounded-lg">
            <Package className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-tertiary uppercase tracking-wider">Total Assets</p>
            <p className="text-2xl font-bold text-secondary">{totalAssets}</p>
          </div>
        </Card>
        <Card className="p-6 flex items-center gap-4 border-t-4 border-t-warning">
          <div className="p-3 bg-warning/10 text-warning rounded-lg">
            <Wrench className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-tertiary uppercase tracking-wider">Active Maintenance</p>
            <p className="text-2xl font-bold text-secondary">{activeMaintenance}</p>
          </div>
        </Card>
        <Card className="p-6 flex items-center gap-4 border-t-4 border-t-error">
          <div className="p-3 bg-error/10 text-error rounded-lg">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-tertiary uppercase tracking-wider">Active Audits</p>
            <p className="text-2xl font-bold text-secondary">{activeAudits}</p>
          </div>
        </Card>
        <Card className="p-6 flex items-center gap-4 border-t-4 border-t-success">
          <div className="p-3 bg-success/10 text-success rounded-lg">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-tertiary uppercase tracking-wider">System Status</p>
            <p className="text-2xl font-bold text-secondary">Healthy</p>
          </div>
        </Card>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-2">
              <span className="text-sm">Asset AF-0012 allocated to Desk 4B</span>
              <span className="text-xs text-tertiary">2 hrs ago</span>
            </div>
            <div className="flex items-center justify-between border-b border-border pb-2">
              <span className="text-sm">Maintenance approved for AF-0018</span>
              <span className="text-xs text-tertiary">5 hrs ago</span>
            </div>
          </div>
        </Card>
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Quick Links</h2>
          <div className="grid grid-cols-2 gap-4">
            <button className="p-4 border border-border rounded-lg text-sm font-medium hover:bg-gray-50 text-left">
              + Register New Asset
            </button>
            <button className="p-4 border border-border rounded-lg text-sm font-medium hover:bg-gray-50 text-left">
              + Request Maintenance
            </button>
          </div>
        </Card>
      </div>
    </div>
  );
}
