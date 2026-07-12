import React, { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { api, buildXml } from '../api/client';
import { AlertTriangle, Plus, UserPlus } from 'lucide-react';

export default function Audit() {
  const [cycles, setCycles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    fetchCycles();
  }, []);

  const fetchCycles = async () => {
    try {
      setLoading(true);
      const doc = await api.get('/audit-cycles');
      const cycleNodes = Array.from(doc.querySelectorAll('data > dict'));
      
      const parsedCycles = cycleNodes.map(node => {
        const id = node.querySelector('id')?.textContent;
        const name = node.querySelector('name')?.textContent;
        const status = node.querySelector('status')?.textContent;
        const scopeDept = node.querySelector('scope_department_id')?.textContent;
        const scopeLocation = node.querySelector('scope_location')?.textContent;
        const startDate = node.querySelector('start_date')?.textContent;
        
        const itemNodes = Array.from(node.querySelectorAll('items > dict'));
        const items = itemNodes.map(itemNode => ({
          id: itemNode.querySelector('id')?.textContent,
          asset_id: itemNode.querySelector('asset')?.textContent, // usually id
          verification: itemNode.querySelector('verification')?.textContent,
        }));
        
        return { id, name, status, scopeDept, scopeLocation, startDate, items };
      });
      setCycles(parsedCycles);
    } catch (err) {
      setError("Failed to fetch audit cycles.");
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (itemId, verificationStatus) => {
    try {
      const xml = buildXml('audit_item_update', { verification: verificationStatus });
      await api.patch(`/audit-items/${itemId}`, xml);
      fetchCycles();
    } catch (err) {
      alert(err.message || 'Failed to update audit item');
    }
  };

  const handleCloseCycle = async (cycleId) => {
    try {
      await api.post(`/audit-cycles/${cycleId}/close`, '');
      fetchCycles();
      alert('Cycle closed successfully. Discrepancy report generated if there were missing/damaged items.');
    } catch (err) {
      alert(err.message || 'Failed to close cycle');
    }
  };
  
  const [showStartCycle, setShowStartCycle] = useState(false);
  const [newCycle, setNewCycle] = useState({ name: '', scope_department_id: '', scope_location: '', start_date: '', end_date: '' });

  const handleStartCycle = async (e) => {
    e.preventDefault();
    try {
      const xml = buildXml('audit_cycle', newCycle);
      await api.post('/audit-cycles', xml);
      setShowStartCycle(false);
      setNewCycle({ name: '', scope_department_id: '', scope_location: '', start_date: '', end_date: '' });
      fetchCycles();
    } catch (err) {
      alert(err.message || 'Failed to start cycle');
    }
  };

  const activeCycles = cycles.filter(c => c.status === 'open');

  return (
    <div className="flex flex-col gap-6 max-w-5xl mx-auto relative">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-secondary">Asset Audit</h1>
          <p className="text-tertiary">Run physical verification cycles for assigned locations.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" className="flex items-center gap-2">
             <UserPlus className="w-4 h-4" /> Assign Auditors
          </Button>
          <Button className="flex items-center gap-2" onClick={() => setShowStartCycle(true)}>
             <Plus className="w-4 h-4" /> Start Cycle
          </Button>
        </div>
      </div>

      {error && <div className="p-4 bg-error-container text-error">{error}</div>}
      {loading && <div className="p-4 text-tertiary">Loading audit cycles...</div>}

      {!loading && activeCycles.length === 0 && (
         <Card className="p-8 text-center text-tertiary">
            No active audit cycles.
         </Card>
      )}

      {!loading && activeCycles.map(cycle => (
        <div key={cycle.id} className="space-y-4">
          <div className="p-4 bg-gray-50 border border-border rounded flex justify-between items-center">
            <p className="font-semibold text-secondary">
              Audit Cycle Active: {cycle.name} | Started: {cycle.startDate?.split('T')[0]} 
              {cycle.scopeDept ? ` | Dept: ${cycle.scopeDept}` : ''}
              {cycle.scopeLocation ? ` | Loc: ${cycle.scopeLocation}` : ''}
            </p>
            <Button onClick={() => handleCloseCycle(cycle.id)}>Close Audit Cycle</Button>
          </div>

          <Card>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-sm">
                <thead>
                  <tr className="border-b border-border bg-gray-50">
                    <th className="p-4 font-semibold text-tertiary uppercase tracking-wider text-xs">Asset ID</th>
                    <th className="p-4 font-semibold text-tertiary uppercase tracking-wider text-xs">Status</th>
                    <th className="p-4 font-semibold text-tertiary uppercase tracking-wider text-xs">Verification</th>
                  </tr>
                </thead>
                <tbody>
                  {cycle.items.map((item) => (
                    <tr key={item.id} className="border-b border-border hover:bg-gray-50">
                      <td className="p-4 font-medium text-primary">Asset: {item.asset_id}</td>
                      <td className="p-4 uppercase text-xs font-semibold">{item.verification}</td>
                      <td className="p-4">
                        <div className="flex gap-2">
                          <button 
                            onClick={() => handleVerify(item.id, 'verified')}
                            className={`px-3 py-1 text-xs font-semibold rounded border ${item.verification === 'verified' ? 'bg-success/10 text-success border-success/30' : 'bg-white text-secondary border-border hover:bg-gray-50'}`}>
                            Verified
                          </button>
                          <button 
                            onClick={() => handleVerify(item.id, 'missing')}
                            className={`px-3 py-1 text-xs font-semibold rounded border ${item.verification === 'missing' ? 'bg-error/10 text-error border-error/30' : 'bg-white text-secondary border-border hover:bg-gray-50'}`}>
                            Missing
                          </button>
                          <button 
                            onClick={() => handleVerify(item.id, 'damaged')}
                            className={`px-3 py-1 text-xs font-semibold rounded border ${item.verification === 'damaged' ? 'bg-warning/10 text-warning border-warning/30' : 'bg-white text-secondary border-border hover:bg-gray-50'}`}>
                            Damaged
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {cycle.items.length === 0 && (
                     <tr><td colSpan="3" className="p-4 text-center text-tertiary">No items in this cycle.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      ))}

      <div className="p-4 bg-error-container text-error border border-error/20 rounded flex items-center justify-between">
        <div className="flex gap-3 items-center">
          <AlertTriangle className="w-5 h-5" />
          <p className="text-sm font-medium">1 asset flagged – discrepancy report generated automatically</p>
        </div>
        <Button variant="secondary" className="bg-white">View Report</Button>
      </div>

      {showStartCycle && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-lg p-6 max-h-screen overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold">Start Audit Cycle</h2>
              <button onClick={() => setShowStartCycle(false)} className="text-tertiary hover:text-secondary">
                <span className="text-lg font-bold">X</span>
              </button>
            </div>
            <form onSubmit={handleStartCycle} className="flex flex-col gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Cycle Name</label>
                <input required type="text" className="w-full p-2 border rounded" value={newCycle.name} onChange={e => setNewCycle({...newCycle, name: e.target.value})} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Scope Dept ID (Optional)</label>
                  <input type="text" className="w-full p-2 border rounded" value={newCycle.scope_department_id} onChange={e => setNewCycle({...newCycle, scope_department_id: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Scope Location (Optional)</label>
                  <input type="text" className="w-full p-2 border rounded" value={newCycle.scope_location} onChange={e => setNewCycle({...newCycle, scope_location: e.target.value})} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Start Date</label>
                  <input required type="date" className="w-full p-2 border rounded" value={newCycle.start_date} onChange={e => setNewCycle({...newCycle, start_date: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">End Date</label>
                  <input required type="date" className="w-full p-2 border rounded" value={newCycle.end_date} onChange={e => setNewCycle({...newCycle, end_date: e.target.value})} />
                </div>
              </div>
              <div className="flex justify-end gap-3 mt-4">
                <Button variant="secondary" onClick={() => setShowStartCycle(false)} type="button">Cancel</Button>
                <Button type="submit">Start Cycle</Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
}
