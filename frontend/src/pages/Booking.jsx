import React, { useState } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { useData } from '../providers/DataProvider';
import { AlertTriangle, Clock } from 'lucide-react';

export default function Booking() {
  const { initialBookings } = useData();
  const [resource, setResource] = useState('Meeting Room A');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleBook = (e) => {
    e.preventDefault();
    setError('Booking Conflict: Meeting Room A is already booked from 09:00 to 10:00 by Procurement Team.');
    setSuccess('');
  };

  return (
    <div className="flex flex-col gap-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-semibold text-secondary">Resource Booking</h1>
        <p className="text-tertiary">Book shared resources like meeting rooms or company vehicles.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6 col-span-1">
          <h2 className="text-lg font-semibold mb-4">New Booking</h2>
          <form onSubmit={handleBook} className="flex flex-col gap-4">
            <div>
              <label className="block text-sm font-semibold mb-1">Resource</label>
              <select className="w-full p-2 border border-border rounded text-sm" value={resource} onChange={(e) => setResource(e.target.value)}>
                <option>Meeting Room A</option>
                <option>Meeting Room B</option>
                <option>Company Van</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold mb-1">Date</label>
              <input type="date" className="w-full p-2 border border-border rounded text-sm" defaultValue="2026-10-14" />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-1">Time</label>
              <div className="flex gap-2">
                <input type="time" className="w-full p-2 border border-border rounded text-sm" defaultValue="09:30" />
                <span className="self-center">-</span>
                <input type="time" className="w-full p-2 border border-border rounded text-sm" defaultValue="10:30" />
              </div>
            </div>
            <Button type="submit" className="mt-2">Confirm Booking</Button>
          </form>

          {error && (
            <div className="mt-4 p-3 bg-error-container text-error text-sm rounded flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
              <p>{error}</p>
            </div>
          )}
        </Card>

        <Card className="p-6 col-span-2">
          <h2 className="text-lg font-semibold mb-4">Schedule: {resource}</h2>
          <div className="space-y-3">
            {initialBookings.map((b) => (
              <div key={b.id} className={`p-4 border rounded flex items-center gap-4 ${b.status === 'conflict' ? 'bg-error/5 border-error/20 border-dashed' : 'bg-primary/5 border-primary/20'}`}>
                <div className="flex items-center gap-2 text-tertiary min-w-24">
                  <Clock className="w-4 h-4" />
                  <span className="text-sm font-medium">{b.start} - {b.end}</span>
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-secondary">{b.user}</p>
                </div>
                {b.status === 'conflict' && (
                  <span className="text-xs font-bold text-error uppercase">Conflict</span>
                )}
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
