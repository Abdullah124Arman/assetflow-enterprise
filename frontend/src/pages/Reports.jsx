import React, { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { Download } from 'lucide-react';
import { api } from '../api/client';

export default function Reports() {
  const [utilization, setUtilization] = useState([]);
  const [maintenanceFreq, setMaintenanceFreq] = useState([]);
  const [idleAssets, setIdleAssets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const [utilDoc, mainDoc, idleDoc] = await Promise.all([
        api.get('/reports/utilization'),
        api.get('/reports/maintenance-frequency'),
        api.get('/reports/idle-assets')
      ]);

      const utilItems = Array.from(utilDoc.querySelectorAll('categories > category > dict')).map(n => ({
        name: n.querySelector('name')?.textContent,
        utilization_percentage: parseFloat(n.querySelector('utilization_percentage')?.textContent || '0')
      }));
      setUtilization(utilItems);

      const mainItems = Array.from(mainDoc.querySelectorAll('assets > asset > dict')).map(n => ({
        name: n.querySelector('name')?.textContent,
        maintenance_count: n.querySelector('maintenance_count')?.textContent
      }));
      setMaintenanceFreq(mainItems);

      const idleItems = Array.from(idleDoc.querySelectorAll('assets > asset > dict')).map(n => ({
        name: n.querySelector('name')?.textContent,
        days_idle: n.querySelector('days_idle')?.textContent
      }));
      setIdleAssets(idleItems);

    } catch (err) {
      console.error('Failed to fetch reports', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    alert("Export functionality triggers XML download. (Not implemented in demo UI)");
  };

  if (loading) return <div className="p-8 text-tertiary">Loading reports...</div>;

  return (
    <div className="flex flex-col gap-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-secondary">Reports & Analytics</h1>
          <p className="text-tertiary">Insights into asset utilization and system health.</p>
        </div>
        <Button className="flex items-center gap-2" onClick={handleExport}>
          <Download className="w-4 h-4" /> Export Report
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6 h-64 flex flex-col">
          <h2 className="text-lg font-semibold mb-4">Utilization by Category</h2>
          <div className="flex-1 flex items-end justify-around pb-4">
            {utilization.slice(0, 4).map((item, i) => (
               <div key={i} className="w-12 bg-primary/60 rounded-t relative" style={{ height: `${Math.max(item.utilization_percentage, 5)}%` }}>
                 <span className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs truncate w-16 text-center">{item.name?.substring(0,4)}</span>
               </div>
            ))}
            {utilization.length === 0 && <p className="text-tertiary text-sm">No utilization data.</p>}
          </div>
        </Card>
        <Card className="p-6 h-64 flex flex-col">
          <h2 className="text-lg font-semibold mb-4">Most Maintained Assets</h2>
          <div className="space-y-4 overflow-y-auto">
            {maintenanceFreq.slice(0, 4).map((item, i) => (
              <div key={i} className="flex justify-between border-b border-border pb-2 text-sm">
                <span className="font-medium text-secondary">{item.name}</span>
                <span className="text-warning font-semibold">{item.maintenance_count} repairs</span>
              </div>
            ))}
            {maintenanceFreq.length === 0 && <p className="text-tertiary text-sm">No maintenance data.</p>}
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Idle Assets</h2>
          <div className="space-y-4">
            {idleAssets.slice(0, 5).map((item, i) => (
              <div key={i} className="flex justify-between border-b border-border pb-2 text-sm">
                <span className="font-medium text-secondary">{item.name}</span>
                <span className="text-tertiary">{item.days_idle} days idle</span>
              </div>
            ))}
            {idleAssets.length === 0 && <p className="text-tertiary text-sm">No idle assets.</p>}
          </div>
        </Card>
      </div>
    </div>
  );
}
