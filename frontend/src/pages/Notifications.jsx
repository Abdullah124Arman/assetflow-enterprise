import React from 'react';
import Card from '../components/ui/Card';
import { AlertTriangle, CheckCircle, CalendarX } from 'lucide-react';

export default function Notifications() {
  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-semibold text-secondary">Activity Logs & Notifications</h1>
        <p className="text-tertiary">System alerts and tracking events.</p>
      </div>

      <div className="flex gap-4 border-b border-border pb-2">
        <button className="text-sm font-semibold text-primary border-b-2 border-primary px-2 pb-1">All</button>
        <button className="text-sm font-medium text-tertiary hover:text-secondary px-2 pb-1">Alerts</button>
        <button className="text-sm font-medium text-tertiary hover:text-secondary px-2 pb-1">Approvals</button>
        <button className="text-sm font-medium text-tertiary hover:text-secondary px-2 pb-1">Bookings</button>
      </div>

      <div className="space-y-4">
        <Card className="p-4 flex gap-4 items-start border-l-4 border-l-error">
          <div className="p-2 bg-error/10 text-error rounded-full shrink-0">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div className="flex-1">
            <div className="flex justify-between">
              <h3 className="font-semibold text-secondary">Overdue Return</h3>
              <span className="text-xs text-tertiary">1d ago</span>
            </div>
            <p className="text-sm text-secondary mt-1">AF-0021 was due 3 days ago. Holder: Michael Scott.</p>
            <button className="mt-3 text-xs font-semibold text-primary hover:underline">Send Reminder</button>
          </div>
        </Card>

        <Card className="p-4 flex gap-4 items-start border-l-4 border-l-success">
          <div className="p-2 bg-success/10 text-success rounded-full shrink-0">
            <CheckCircle className="w-5 h-5" />
          </div>
          <div className="flex-1">
            <div className="flex justify-between">
              <h3 className="font-semibold text-secondary">Maintenance Approved</h3>
              <span className="text-xs text-tertiary">2h ago</span>
            </div>
            <p className="text-sm text-secondary mt-1">AF-0012 Keyboard sticky request approved.</p>
            <button className="mt-3 text-xs font-semibold text-primary hover:underline">Track Progress</button>
          </div>
        </Card>

        <Card className="p-4 flex gap-4 items-start border-l-4 border-l-warning">
          <div className="p-2 bg-warning/10 text-warning rounded-full shrink-0">
            <CalendarX className="w-5 h-5" />
          </div>
          <div className="flex-1">
            <div className="flex justify-between">
              <h3 className="font-semibold text-secondary">Booking Conflict</h3>
              <span className="text-xs text-tertiary">5m ago</span>
            </div>
            <p className="text-sm text-secondary mt-1">Meeting Room A requested by Marketing overlaps with Procurement Team.</p>
            <button className="mt-3 text-xs font-semibold text-primary hover:underline">Resolve Conflict</button>
          </div>
        </Card>
      </div>
    </div>
  );
}
