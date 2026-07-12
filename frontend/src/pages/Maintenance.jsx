import React from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { useData } from '../providers/DataProvider';

export default function Maintenance() {
  const { maintenance } = useData();

  const Column = ({ title, items, actionLabel, actionStyle = 'primary' }) => (
    <div className="flex flex-col gap-3 min-w-72">
      <h3 className="font-semibold text-secondary border-b border-border pb-2">{title} <span className="text-tertiary font-normal text-sm ml-2">({items.length})</span></h3>
      <div className="flex flex-col gap-3">
        {items.map(item => (
          <Card key={item.id} className="p-4 cursor-pointer hover:shadow-md transition-shadow border-t-4 border-t-warning">
            <div className="flex justify-between items-start mb-2">
              <span className="font-bold text-primary text-sm">{item.id}</span>
              <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                item.urgency === 'High' ? 'bg-error/10 text-error' : item.urgency === 'Medium' ? 'bg-warning/10 text-warning' : 'bg-gray-100 text-gray-600'
              }`}>{item.urgency}</span>
            </div>
            <p className="text-sm text-secondary font-medium mb-4">{item.summary}</p>
            {item.tech && <p className="text-xs text-tertiary mb-3">Tech: {item.tech}</p>}
            {actionLabel && (
              <Button variant={actionStyle} className="w-full text-xs py-1.5">{actionLabel}</Button>
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
        <Button>+ Raise Request</Button>
      </div>
      
      <div className="flex-1 flex gap-6 overflow-x-auto pb-4">
        <Column title="Pending Approval" items={maintenance.pending} actionLabel="Approve" actionStyle="primary" />
        <Column title="Approved (Awaiting Tech)" items={maintenance.approved} actionLabel="Assign Tech" actionStyle="secondary" />
        <Column title="In Progress" items={maintenance.inProgress} actionLabel="Mark Resolved" actionStyle="secondary" />
        <Column title="Resolved" items={maintenance.resolved} />
      </div>
    </div>
  );
}
