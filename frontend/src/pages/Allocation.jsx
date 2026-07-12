import React, { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import StatusChip from '../components/ui/StatusChip';
import { AlertTriangle, ArrowRight } from 'lucide-react';
import { api, buildXml } from '../api/client';

export default function Allocation() {
  const [assets, setAssets] = useState([]);
  const [selectedAssetId, setSelectedAssetId] = useState('');
  const [assignee, setAssignee] = useState('');
  const [expectedReturnDate, setExpectedReturnDate] = useState('');
  const [transferReason, setTransferReason] = useState('');
  const [transferTo, setTransferTo] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [conflictHolder, setConflictHolder] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAssets();
  }, []);

  useEffect(() => {
    if (selectedAssetId) {
      fetchHistory(selectedAssetId);
      setConflictHolder(null);
      setError('');
      setSuccess('');
    }
  }, [selectedAssetId]);

  const fetchAssets = async () => {
    try {
      const doc = await api.get('/assets');
      const items = Array.from(doc.querySelectorAll('asset')).map(node => ({
        id: node.querySelector('tag')?.textContent || node.querySelector('id')?.textContent,
        name: node.querySelector('name')?.textContent,
        status: node.querySelector('status')?.textContent,
        holder: node.querySelector('holder')?.textContent,
        department: node.querySelector('department')?.textContent,
      }));
      setAssets(items);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchHistory = async (id) => {
    try {
      const doc = await api.get(`/assets/${id}/history`);
      const items = Array.from(doc.querySelectorAll('history_entry')).map(node => ({
        date: node.querySelector('date')?.textContent,
        event: node.querySelector('event')?.textContent,
        user: node.querySelector('user')?.textContent,
      }));
      setHistory(items);
    } catch (e) {
      console.error(e);
    }
  };

  const selectedAsset = assets.find(a => a.id === selectedAssetId);

  const handleAllocate = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setConflictHolder(null);
    setLoading(true);

    try {
      const xml = buildXml('allocation_request', { asset_id: selectedAssetId, assignee, expected_return_date: expectedReturnDate });
      await api.post('/allocations', xml);
      setSuccess('Successfully allocated.');
      fetchAssets();
      fetchHistory(selectedAssetId);
      setAssignee('');
      setExpectedReturnDate('');
    } catch (err) {
      if (err.code === 'ALREADY_ALLOCATED') {
        // We assume the API returns details about who currently holds it
        const holder = err.details || selectedAsset?.holder || 'Unknown';
        const dept = selectedAsset?.department || 'Unknown';
        setConflictHolder({ holder, dept });
        setError(`Already Allocated to ${holder} (${dept}) — Direct re-allocation is blocked.`);
      } else {
        setError(err.message || 'Failed to allocate asset.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleTransfer = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const xml = buildXml('transfer_request', { asset_id: selectedAssetId, transfer_to: transferTo, reason: transferReason });
      await api.post('/transfer-requests', xml);
      setSuccess('Transfer request submitted successfully.');
      setTransferTo('');
      setTransferReason('');
    } catch (err) {
      setError(err.message || 'Failed to submit transfer request.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-semibold text-secondary">Allocation & Transfer</h1>
        <p className="text-tertiary">Assign assets to employees or request transfers.</p>
      </div>

      <Card className="p-6">
        <div className="mb-6">
          <label className="block text-sm font-semibold mb-2">Select Asset</label>
          <select 
            className="w-full p-2 border border-border rounded text-sm focus:outline-none focus:border-primary"
            value={selectedAssetId}
            onChange={(e) => setSelectedAssetId(e.target.value)}
          >
            <option value="">-- Choose an Asset --</option>
            {assets.map(a => (
              <option key={a.id} value={a.id}>{a.id} - {a.name} ({a.status})</option>
            ))}
          </select>
        </div>

        {selectedAsset && (
          <div className="p-4 bg-gray-50 border border-border rounded flex items-center justify-between mb-6">
            <div>
              <p className="text-sm font-semibold">{selectedAsset.name}</p>
            </div>
            <StatusChip status={selectedAsset.status} />
          </div>
        )}

        {error && (
          <div className="p-4 bg-error-container text-error border border-error/20 rounded flex gap-3 items-start mb-6">
            <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5 text-error" />
            <p className="text-sm font-medium">{error}</p>
          </div>
        )}

        {success && (
          <div className="p-4 bg-success/10 text-success border border-success/20 rounded text-sm font-medium mb-6">
            {success}
          </div>
        )}

        {selectedAsset && !conflictHolder && (
          <form onSubmit={handleAllocate} className="flex flex-col gap-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold mb-2">Assignee</label>
                <input 
                  type="text" 
                  required
                  placeholder="e.g., employee_id or name"
                  className="w-full p-2 border border-border rounded text-sm focus:outline-none focus:border-primary"
                  value={assignee}
                  onChange={(e) => setAssignee(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-semibold mb-2">Expected Return Date</label>
                <input 
                  type="date" 
                  className="w-full p-2 border border-border rounded text-sm focus:outline-none focus:border-primary"
                  value={expectedReturnDate}
                  onChange={(e) => setExpectedReturnDate(e.target.value)}
                />
              </div>
            </div>
            <div className="flex pt-4 border-t border-border">
              <Button type="submit" disabled={loading}>Allocate Asset</Button>
            </div>
          </form>
        )}

        {selectedAsset && conflictHolder && (
          <form onSubmit={handleTransfer} className="flex flex-col gap-6 bg-red-50 p-4 rounded border border-red-100 mt-4">
            <h3 className="font-semibold text-error">Transfer Request</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold mb-2">Transfer From</label>
                <input 
                  type="text" 
                  disabled
                  value={`${conflictHolder.holder} (${conflictHolder.dept})`}
                  className="w-full p-2 border border-border rounded text-sm bg-gray-100"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold mb-2">Transfer To</label>
                <input 
                  type="text" 
                  required
                  className="w-full p-2 border border-border rounded text-sm focus:outline-none focus:border-primary"
                  value={transferTo}
                  onChange={(e) => setTransferTo(e.target.value)}
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Reason</label>
              <textarea 
                required
                className="w-full p-2 border border-border rounded text-sm focus:outline-none focus:border-primary"
                value={transferReason}
                onChange={(e) => setTransferReason(e.target.value)}
              />
            </div>
            <div className="flex pt-2">
              <Button type="submit" disabled={loading} className="flex items-center gap-2">
                Submit Transfer Request <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
          </form>
        )}
      </Card>

      {selectedAsset && (
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">History</h2>
          {history.length > 0 ? (
            <div className="space-y-4">
              {history.map((h, i) => (
                <div key={i} className="flex justify-between items-center border-b border-border pb-2 text-sm">
                  <div>
                    <span className="font-medium text-secondary">{h.event}</span> by {h.user}
                  </div>
                  <span className="text-tertiary">{h.date}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-tertiary">No history available for this asset.</p>
          )}
        </Card>
      )}
    </div>
  );
}
