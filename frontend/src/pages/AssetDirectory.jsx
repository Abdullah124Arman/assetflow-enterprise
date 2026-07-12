import React from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import StatusChip from '../components/ui/StatusChip';
import { useData } from '../providers/DataProvider';
import { Plus, Filter, Download } from 'lucide-react';

export default function AssetDirectory() {
  const { assets } = useData();

  return (
    <div className="flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-secondary">Asset Directory</h1>
          <p className="text-tertiary">Manage and track all company assets.</p>
        </div>
        <div className="flex gap-3">
          <Button variant="secondary" className="flex items-center gap-2">
            <Filter className="w-4 h-4" /> Filter
          </Button>
          <Button variant="secondary" className="flex items-center gap-2">
            <Download className="w-4 h-4" /> Export
          </Button>
          <Button className="flex items-center gap-2">
            <Plus className="w-4 h-4" /> Register Asset
          </Button>
        </div>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b border-border bg-gray-50">
                <th className="p-4 font-semibold text-tertiary uppercase tracking-wider text-xs">Asset ID</th>
                <th className="p-4 font-semibold text-tertiary uppercase tracking-wider text-xs">Name</th>
                <th className="p-4 font-semibold text-tertiary uppercase tracking-wider text-xs">Category</th>
                <th className="p-4 font-semibold text-tertiary uppercase tracking-wider text-xs">Location</th>
                <th className="p-4 font-semibold text-tertiary uppercase tracking-wider text-xs">Status</th>
              </tr>
            </thead>
            <tbody>
              {assets.map((asset) => (
                <tr key={asset.id} className="border-b border-border hover:bg-gray-50">
                  <td className="p-4 font-medium text-primary cursor-pointer">{asset.id}</td>
                  <td className="p-4">{asset.name}</td>
                  <td className="p-4">{asset.category}</td>
                  <td className="p-4">{asset.location}</td>
                  <td className="p-4">
                    <StatusChip status={asset.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
