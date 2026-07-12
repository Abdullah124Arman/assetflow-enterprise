import React, { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { AlertTriangle, Clock } from 'lucide-react';
import { api, buildXml } from '../api/client';

export default function Booking() {
  const [resource, setResource] = useState('AF-0010'); // Assume resource is an asset ID for now, ideally fetched from assets
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [startTime, setStartTime] = useState('09:00');
  const [endTime, setEndTime] = useState('10:00');
  const [purpose, setPurpose] = useState('');
  
  const [bookings, setBookings] = useState([]);
  const [conflictBooking, setConflictBooking] = useState(null);
  
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchBookings();
    setConflictBooking(null);
    setError('');
    setSuccess('');
  }, [resource, date]);

  const fetchBookings = async () => {
    try {
      const doc = await api.get(`/bookings?resource_id=${resource}&date=${date}`);
      const items = Array.from(doc.querySelectorAll('booking')).map(node => ({
        id: node.querySelector('id')?.textContent,
        start_time: node.querySelector('start_time')?.textContent,
        end_time: node.querySelector('end_time')?.textContent,
        purpose: node.querySelector('purpose')?.textContent,
        user: node.querySelector('user_name')?.textContent,
      }));
      setBookings(items);
    } catch (e) {
      console.error("Failed to fetch bookings", e);
    }
  };

  const handleBook = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setConflictBooking(null);
    setLoading(true);

    try {
      // Need full timestamps for backend
      const startIso = new Date(`${date}T${startTime}:00`).toISOString();
      const endIso = new Date(`${date}T${endTime}:00`).toISOString();
      
      const xml = buildXml('booking_request', {
        resource_asset_id: resource,
        start_time: startIso,
        end_time: endIso,
        purpose
      });
      
      await api.post('/bookings', xml);
      setSuccess('Booking confirmed.');
      setPurpose('');
      fetchBookings();
    } catch (err) {
      if (err.code === 'SLOT_UNAVAILABLE') {
        setError(`Requested ${startTime} to ${endTime} – conflict – slot is unavailable.`);
        setConflictBooking({ start: startTime, end: endTime, user: 'Conflict' });
      } else {
        setError(err.message || 'Failed to book slot.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Convert ISO timestamps to HH:MM for display in the schedule
  const formatTime = (isoString) => {
    if (!isoString) return '';
    const dateObj = new Date(isoString);
    return dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
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
              <label className="block text-sm font-semibold mb-1">Resource ID</label>
              <input 
                type="text" 
                className="w-full p-2 border border-border rounded text-sm" 
                value={resource} 
                onChange={(e) => setResource(e.target.value)} 
                required 
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-1">Date</label>
              <input type="date" className="w-full p-2 border border-border rounded text-sm" value={date} onChange={(e) => setDate(e.target.value)} required />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-1">Time</label>
              <div className="flex gap-2">
                <input type="time" className="w-full p-2 border border-border rounded text-sm" value={startTime} onChange={(e) => setStartTime(e.target.value)} required />
                <span className="self-center">-</span>
                <input type="time" className="w-full p-2 border border-border rounded text-sm" value={endTime} onChange={(e) => setEndTime(e.target.value)} required />
              </div>
            </div>
            <div>
              <label className="block text-sm font-semibold mb-1">Purpose</label>
              <input type="text" className="w-full p-2 border border-border rounded text-sm" value={purpose} onChange={(e) => setPurpose(e.target.value)} required />
            </div>
            
            <Button type="submit" disabled={loading} className="mt-2">
              Book a Slot
            </Button>
          </form>

          {success && (
            <div className="mt-4 p-3 bg-success/10 text-success text-sm rounded border border-success/20 font-medium">
              {success}
            </div>
          )}

          {error && (
            <div className="mt-4 p-3 bg-error-container text-error text-sm rounded flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
              <p>{error}</p>
            </div>
          )}
        </Card>

        <Card className="p-6 col-span-2">
          <h2 className="text-lg font-semibold mb-4">Schedule: {resource} on {date}</h2>
          <div className="space-y-3">
            {bookings.length === 0 && !conflictBooking && (
              <p className="text-sm text-tertiary">No bookings for this date.</p>
            )}
            
            {bookings.map((b, i) => (
              <div key={b.id || i} className="p-4 border rounded flex items-center gap-4 bg-primary/5 border-primary/20">
                <div className="flex items-center gap-2 text-tertiary min-w-24">
                  <Clock className="w-4 h-4" />
                  <span className="text-sm font-medium">{formatTime(b.start_time)} - {formatTime(b.end_time)}</span>
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-secondary">Booked – {b.user || 'Unknown'} – {b.purpose}</p>
                </div>
              </div>
            ))}

            {conflictBooking && (
              <div className="p-4 border rounded flex items-center gap-4 bg-error/5 border-error/20 border-dashed">
                <div className="flex items-center gap-2 text-tertiary min-w-24">
                  <Clock className="w-4 h-4" />
                  <span className="text-sm font-medium text-error">{conflictBooking.start} - {conflictBooking.end}</span>
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-error">Requested slot is unavailable</p>
                </div>
                <span className="text-xs font-bold text-error uppercase">Conflict</span>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
