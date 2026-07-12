import React, { useState } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import StatusChip from '../components/ui/StatusChip';
import { useData } from '../providers/DataProvider';
import { AlertTriangle, ArrowRight } from 'lucide-react';

export default function Allocation() {
  const { assets, setAssets } = useData();
  const [selectedAssetId, setSelectedAssetId] = useState('');
  const [assignee, setAssignee] = useState('');
  const [location, setLocation] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const selectedAsset = assets.find(a => a.id === selectedAssetId);

  const handleAllocate = (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!selectedAsset) return;

    if (selectedAsset.status === 'Allocated') {
      setError(`Cannot allocate ${selectedAsset.id} (${selectedAsset.name}). It is already allocated to ${selectedAsset.holder} at ${selectedAsset.location}. Please submit a Transfer Request instead.`);
      return;
    }

    const updatedAssets = assets.map(a => 
      a.id === selectedAsset.id 
        ? { ...a, status: 'Allocated', holder: assignee, location: location }
        : a
    );
    
    setAssets(updatedAssets);
    setSuccess(`Successfully allocated ${selectedAsset.name} to ${assignee}.`);
    setAssignee('');
    setLocation('');
  };

  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-semibold text-secondary">Allocation & Transfer</h1>
        <p className="text-tertiary">Assign assets to employees or locations.</p>
      </div>

      <Card className="p-6">
        <form onSubmit={handleAllocate} className="flex flex-col gap-6">
          
          <div>
            <label className="block text-sm font-semibold mb-2">Select Asset</label>
            <select 
              className="w-full p-2 border border-border rounded text-sm focus:outline-none focus:border-primary"
              value={selectedAssetId}
              onChange={(e) => {
                setSelectedAssetId(e.target.value);
                setError('');
                setSuccess('');
              }}
            >
              <option value="">-- Choose an Asset --</option>
              {assets.map(a => (
                <option key={a.id} value={a.id}>{a.id} - {a.name} ({a.status})</option>
              ))}
            </select>
          </div>

          {selectedAsset && (
            <div className="p-4 bg-gray-50 border border-border rounded flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold">{selectedAsset.name}</p>
                <p className="text-xs text-tertiary">Current Location: {selectedAsset.location}</p>
              </div>
              <StatusChip status={selectedAsset.status} />
            </div>
          )}

          {error && (
            <div className="p-4 bg-error-container text-error border border-error/20 rounded flex gap-3 items-start">
              <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5 text-error" />
              <p className="text-sm font-medium">{error}</p>
            </div>
          )}

          {success && (
            <div className="p-4 bg-success/10 text-success border border-success/20 rounded text-sm font-medium">
              {success}
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-2">Assignee (Employee)</label>
              <input 
                type="text" 
                required
                placeholder="e.g., John Doe"
                className="w-full p-2 border border-border rounded text-sm focus:outline-none focus:border-primary"
                value={assignee}
                onChange={(e) => setAssignee(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Location</label>
              <input 
                type="text" 
                required
                placeholder="e.g., Desk 5A"
                className="w-full p-2 border border-border rounded text-sm focus:outline-none focus:border-primary"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
              />
            </div>
          </div>

          <div className="flex gap-4 pt-4 border-t border-border">
            <Button type="submit" className="flex items-center gap-2">
              Allocate Asset
            </Button>
            {error && (
              <Button type="button" variant="secondary" className="flex items-center gap-2">
                Initiate Transfer Request <ArrowRight className="w-4 h-4" />
              </Button>
            )}
          </div>
        </form>
      </Card>
    </div>
  );
}
