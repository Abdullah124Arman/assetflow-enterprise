import React, { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import StatusChip from '../components/ui/StatusChip';
import { Plus, Filter, Download, X } from 'lucide-react';
import { api, buildXml } from '../api/client';

export default function AssetDirectory() {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showRegisterForm, setShowRegisterForm] = useState(false);
  const [newAsset, setNewAsset] = useState({ name: '', category: '', location: '', department_id: '', purchase_date: '', acquisition_cost: '' });

  useEffect(() => {
    fetchAssets();
  }, []);

  const fetchAssets = async () => {
    setLoading(true);
    try {
      const doc = await api.get('/assets');
      const items = Array.from(doc.querySelectorAll('asset')).map(node => ({
        id: node.querySelector('tag')?.textContent || node.querySelector('id')?.textContent,
        name: node.querySelector('name')?.textContent,
        category: node.querySelector('category')?.textContent,
        location: node.querySelector('location')?.textContent,
        status: node.querySelector('status')?.textContent,
      }));
      setAssets(items);
    } catch (e) {
      console.error("Failed to fetch assets", e);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const xml = buildXml('asset', newAsset);
      await api.post('/assets', xml);
      setShowRegisterForm(false);
      setNewAsset({ name: '', category: '', location: '', department_id: '', purchase_date: '', acquisition_cost: '' });
      fetchAssets();
    } catch (err) {
      alert(err.message || 'Failed to register asset');
    }
  };

  return (
    <div className="flex flex-col gap-6 relative">
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
          <Button onClick={() => setShowRegisterForm(true)} className="flex items-center gap-2">
            <Plus className="w-4 h-4" /> Register Asset
          </Button>
        </div>
      </div>

      <Card>
        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-8 text-center text-tertiary">Loading assets...</div>
          ) : (
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
                {assets.map((asset, i) => (
                  <tr key={asset.id || i} className="border-b border-border hover:bg-gray-50">
                    <td className="p-4 font-medium text-primary cursor-pointer">{asset.id}</td>
                    <td className="p-4">{asset.name}</td>
                    <td className="p-4">{asset.category}</td>
                    <td className="p-4">{asset.location}</td>
                    <td className="p-4">
                      <StatusChip status={asset.status} />
                    </td>
                  </tr>
                ))}
                {assets.length === 0 && (
                  <tr>
                    <td colSpan="5" className="p-8 text-center text-tertiary">No assets found.</td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </div>
      </Card>

      {showRegisterForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-lg p-6 max-h-screen overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold">Register New Asset</h2>
              <button onClick={() => setShowRegisterForm(false)} className="text-tertiary hover:text-secondary">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleRegister} className="flex flex-col gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Asset Name</label>
                <input required type="text" className="w-full p-2 border rounded" value={newAsset.name} onChange={e => setNewAsset({...newAsset, name: e.target.value})} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Category</label>
                  <input required type="text" className="w-full p-2 border rounded" value={newAsset.category} onChange={e => setNewAsset({...newAsset, category: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Department ID</label>
                  <input type="number" className="w-full p-2 border rounded" value={newAsset.department_id} onChange={e => setNewAsset({...newAsset, department_id: e.target.value})} />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Location</label>
                <input type="text" className="w-full p-2 border rounded" value={newAsset.location} onChange={e => setNewAsset({...newAsset, location: e.target.value})} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Purchase Date</label>
                  <input type="date" className="w-full p-2 border rounded" value={newAsset.purchase_date} onChange={e => setNewAsset({...newAsset, purchase_date: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Acquisition Cost</label>
                  <input type="number" step="0.01" className="w-full p-2 border rounded" value={newAsset.acquisition_cost} onChange={e => setNewAsset({...newAsset, acquisition_cost: e.target.value})} />
                </div>
              </div>
              <div className="flex justify-end gap-3 mt-4">
                <Button variant="secondary" onClick={() => setShowRegisterForm(false)} type="button">Cancel</Button>
                <Button type="submit">Register Asset</Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
}
