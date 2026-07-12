import React from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { useData } from '../providers/DataProvider';
import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

export default function Audit() {
  const { initialAudit } = useData();

  return (
    <div className="flex flex-col gap-6 max-w-5xl mx-auto">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-secondary">Asset Audit</h1>
          <p className="text-tertiary">Run physical verification cycles for assigned locations.</p>
        </div>
        <Button>Close Audit Cycle</Button>
      </div>

      <div className="p-4 bg-gray-50 border border-border rounded flex justify-between items-center">
        <p className="font-semibold text-secondary">Audit Cycle Active: IT Department (Oct 1 - Oct 15) | Auditors: S. Lee, M. Chen</p>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b border-border bg-gray-50">
                <th className="p-4 font-semibold text-tertiary uppercase tracking-wider text-xs">Asset Tag</th>
                <th className="p-4 font-semibold text-tertiary uppercase tracking-wider text-xs">Asset Name</th>
                <th className="p-4 font-semibold text-tertiary uppercase tracking-wider text-xs">Expected Location</th>
                <th className="p-4 font-semibold text-tertiary uppercase tracking-wider text-xs">Verification</th>
              </tr>
            </thead>
            <tbody>
              {initialAudit.map((item) => (
                <tr key={item.id} className="border-b border-border hover:bg-gray-50">
                  <td className="p-4 font-medium text-primary">{item.id}</td>
                  <td className="p-4">{item.name}</td>
                  <td className="p-4">{item.location}</td>
                  <td className="p-4">
                    <div className="flex gap-2">
                      <button className={`px-3 py-1 text-xs font-semibold rounded border ${item.verification === 'verified' ? 'bg-success/10 text-success border-success/30' : 'bg-white text-secondary border-border hover:bg-gray-50'}`}>
                        Verified
                      </button>
                      <button className={`px-3 py-1 text-xs font-semibold rounded border ${item.verification === 'missing' ? 'bg-error/10 text-error border-error/30' : 'bg-white text-secondary border-border hover:bg-gray-50'}`}>
                        Missing
                      </button>
                      <button className={`px-3 py-1 text-xs font-semibold rounded border ${item.verification === 'damaged' ? 'bg-warning/10 text-warning border-warning/30' : 'bg-white text-secondary border-border hover:bg-gray-50'}`}>
                        Damaged
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <div className="p-4 bg-error-container text-error border border-error/20 rounded flex items-center justify-between">
        <div className="flex gap-3 items-center">
          <AlertTriangle className="w-5 h-5" />
          <p className="text-sm font-medium">1 asset flagged – discrepancy report generated automatically</p>
        </div>
        <Button variant="secondary" className="bg-white">View Report</Button>
      </div>
    </div>
  );
}
