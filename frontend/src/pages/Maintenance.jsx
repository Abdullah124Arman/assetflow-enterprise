import React, { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { api, buildXml } from '../api/client';
import { X } from 'lucide-react';

export default function Maintenance() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [newRequest, setNewRequest] = useState({ asset_id: '', issue: '', priority: 'medium', photo_url: '' });

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const doc = await api.get('/maintenance-requests');
      const items = Array.from(doc.querySelectorAll('maintenance_request')).map(node => ({
        id: node.querySelector('id')?.textContent,
        asset_id: node.querySelector('asset_id')?.textContent,
        issue: node.querySelector('issue')?.textContent,
        priority: node.querySelector('priority')?.textContent || 'medium',
        status: node.querySelector('status')?.textContent,
        technician: node.querySelector('technician_name')?.textContent,
      }));
      setRequests(items);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (id, actionStr, extraData = {}) => {
    try {
      let data = { action: actionStr, ...extraData };
      if (actionStr === 'assign' && !extraData.technician_name) {
        const name = prompt("Enter Technician Name:");
        if (!name) return;
        data.technician_name = name;
      }
      
      const xml = buildXml('maintenance_update', data);
      await api.patch(`/maintenance-requests/${id}`, xml);
      fetchRequests();
    } catch (e) {
      alert(e.message || "Action failed");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const xml = buildXml('maintenance_request', newRequest);
      await api.post('/maintenance-requests', xml);
      setShowForm(false);
      setNewRequest({ asset_id: '', issue: '', priority: 'medium', photo_url: '' });
      fetchRequests();
    } catch (e) {
      alert(e.message || 'Failed to raise request');
    }
  };

  const pending = requests.filter(r => r.status === 'pending');
  const approved = requests.filter(r => r.status === 'approved');
  const assigned = requests.filter(r => r.status === 'technician_assigned');
  const inProgress = requests.filter(r => r.status === 'in_progress');
  const resolved = requests.filter(r => r.status === 'resolved');

  const Column = ({ title, items, actions = [] }) => (
    <div className="flex flex-col gap-3 min-w-72">
      <h3 className="font-semibold text-secondary border-b border-border pb-2">{title} <span className="text-tertiary font-normal text-sm ml-2">({items.length})</span></h3>
      <div className="flex flex-col gap-3">
        {items.map(item => (
          <Card key={item.id} className="p-4 cursor-pointer hover:shadow-md transition-shadow border-t-4 border-t-warning">
            <div className="flex justify-between items-start mb-2">
              <span className="font-bold text-primary text-sm">{item.asset_id}</span>
              <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                item.priority === 'critical' ? 'bg-error/10 text-error' : item.priority === 'high' ? 'bg-error/10 text-error' : 'bg-warning/10 text-warning'
              }`}>{item.priority}</span>
            </div>
            <p className="text-sm text-secondary font-medium mb-4">{item.issue}</p>
            {item.technician && <p className="text-xs text-tertiary mb-3">Tech: {item.technician}</p>}
            {actions.length > 0 && (
              <div className="flex gap-2">
                {actions.map(action => (
                  <Button 
                    key={action.label} 
                    variant={action.variant || 'primary'} 
                    className="flex-1 text-xs py-1.5"
                    onClick={() => handleAction(item.id, action.action)}
                  >
                    {action.label}
                  </Button>
                ))}
              </div>
            )}
          </Card>
        ))}
      </div>
    </div>
  );

  return (
    <div className="flex flex-col h-full gap-6">
      <div className="flex justify-between items-center shrink-0">
        <div>
          <h1 className="text-2xl font-semibold text-secondary">Maintenance Management</h1>
          <p className="text-tertiary">Track repair requests through the resolution lifecycle.</p>
        </div>
        <Button onClick={() => setShowForm(true)}>+ Raise Request</Button>
      </div>
      
      <div className="flex-1 flex gap-6 overflow-x-auto pb-4">
        {loading ? <p className="p-8">Loading...</p> : (
          <>
            <Column 
              title="Pending Approval" 
              items={pending} 
              actions={[{ label: 'Approve', action: 'approve' }, { label: 'Reject', action: 'reject', variant: 'secondary' }]} 
            />
            <Column 
              title="Approved" 
              items={approved} 
              actions={[{ label: 'Assign Tech', action: 'assign' }]} 
            />
            <Column 
              title="Technician Assigned" 
              items={assigned} 
              actions={[{ label: 'Mark In Progress', action: 'in_progress' }]} 
            />
            <Column 
              title="In Progress" 
              items={inProgress} 
              actions={[{ label: 'Mark Resolved', action: 'resolve' }]} 
            />
            <Column 
              title="Resolved" 
              items={resolved} 
            />
          </>
        )}
      </div>
      
      <p className="text-xs text-tertiary text-center pb-4">
        Footnote: Approving a card moves the asset to Under Maintenance, resolving returns it to Available
      </p>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-lg p-6 max-h-screen overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold">Raise Maintenance Request</h2>
              <button onClick={() => setShowForm(false)} className="text-tertiary hover:text-secondary">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Asset ID</label>
                <input required type="text" className="w-full p-2 border rounded" value={newRequest.asset_id} onChange={e => setNewRequest({...newRequest, asset_id: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Issue Description</label>
                <textarea required className="w-full p-2 border rounded" value={newRequest.issue} onChange={e => setNewRequest({...newRequest, issue: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Priority</label>
                <select className="w-full p-2 border rounded" value={newRequest.priority} onChange={e => setNewRequest({...newRequest, priority: e.target.value})}>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Photo URL (Optional)</label>
                <input type="text" className="w-full p-2 border rounded" value={newRequest.photo_url} onChange={e => setNewRequest({...newRequest, photo_url: e.target.value})} />
              </div>
              <div className="flex justify-end gap-3 mt-4">
                <Button variant="secondary" onClick={() => setShowForm(false)} type="button">Cancel</Button>
                <Button type="submit">Submit Request</Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
}
