import React, { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import { api } from '../api/client';
import { Package, Wrench, ShieldCheck, Activity } from 'lucide-react';

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const doc = await api.get('/dashboard/kpis');
      // Parse standard XML
      const kpisNode = doc.querySelector('kpis');
      const kpis = {
        available_assets: kpisNode?.querySelector('available_assets')?.textContent || '0',
        allocated_assets: kpisNode?.querySelector('allocated_assets')?.textContent || '0',
        maintenance_today: kpisNode?.querySelector('maintenance_today')?.textContent || '0',
        pending_transfers: kpisNode?.querySelector('pending_transfers')?.textContent || '0'
      };
      
      const activityNodes = Array.from(doc.querySelectorAll('recent_activity > activity > dict'));
      const activities = activityNodes.map(node => ({
        id: node.querySelector('id')?.textContent,
        action: node.querySelector('action')?.textContent,
        created_at: node.querySelector('created_at')?.textContent
      }));
      
      setData({ kpis, activities });
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-8 text-tertiary">Loading dashboard...</div>;

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
            <p className="text-sm font-medium text-tertiary uppercase tracking-wider">Available Assets</p>
            <p className="text-2xl font-bold text-secondary">{data?.kpis.available_assets}</p>
          </div>
        </Card>
        <Card className="p-6 flex items-center gap-4 border-t-4 border-t-warning">
          <div className="p-3 bg-warning/10 text-warning rounded-lg">
            <Wrench className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-tertiary uppercase tracking-wider">Allocated Assets</p>
            <p className="text-2xl font-bold text-secondary">{data?.kpis.allocated_assets}</p>
          </div>
        </Card>
        <Card className="p-6 flex items-center gap-4 border-t-4 border-t-error">
          <div className="p-3 bg-error/10 text-error rounded-lg">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-tertiary uppercase tracking-wider">Maintenance</p>
            <p className="text-2xl font-bold text-secondary">{data?.kpis.maintenance_today}</p>
          </div>
        </Card>
        <Card className="p-6 flex items-center gap-4 border-t-4 border-t-success">
          <div className="p-3 bg-success/10 text-success rounded-lg">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-tertiary uppercase tracking-wider">Pending Transfers</p>
            <p className="text-2xl font-bold text-secondary">{data?.kpis.pending_transfers}</p>
          </div>
        </Card>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {data?.activities.length > 0 ? data.activities.map(act => (
               <div key={act.id} className="flex items-center justify-between border-b border-border pb-2">
                 <span className="text-sm text-secondary font-medium">{act.action}</span>
                 <span className="text-xs text-tertiary">{new Date(act.created_at).toLocaleString()}</span>
               </div>
            )) : <p className="text-sm text-tertiary">No recent activity.</p>}
          </div>
        </Card>
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Quick Links</h2>
          <div className="grid grid-cols-2 gap-4">
            <a href="/assets" className="p-4 border border-border rounded-lg text-sm font-medium hover:bg-gray-50 text-left block">
              Manage Assets
            </a>
            <a href="/maintenance" className="p-4 border border-border rounded-lg text-sm font-medium hover:bg-gray-50 text-left block">
              Maintenance Board
            </a>
          </div>
        </Card>
      </div>
    </div>
  );
}
