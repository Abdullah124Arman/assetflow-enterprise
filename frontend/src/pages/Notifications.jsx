import React, { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import { AlertTriangle, CheckCircle, CalendarX, Info, Check } from 'lucide-react';
import { api, buildXml } from '../api/client';

export default function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const doc = await api.get('/notifications');
      const nodes = Array.from(doc.querySelectorAll('notifications > notification > dict'));
      const notifs = nodes.map(node => ({
        id: node.querySelector('id')?.textContent,
        type: node.querySelector('type')?.textContent,
        message: node.querySelector('message')?.textContent,
        read: node.querySelector('read')?.textContent === 'True',
        created_at: node.querySelector('created_at')?.textContent
      }));
      setNotifications(notifs);
    } catch (err) {
      console.error('Failed to fetch notifications', err);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (id) => {
    try {
      await api.patch(`/notifications/${id}/read`, buildXml('notification_update', { read: true }));
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
    } catch (err) {
      console.error('Failed to mark read', err);
    }
  };

  const getIcon = (type) => {
    if (type.includes('discrepancy') || type.includes('conflict') || type.includes('overdue')) return <AlertTriangle className="w-5 h-5 text-error" />;
    if (type.includes('approve') || type.includes('assigned')) return <CheckCircle className="w-5 h-5 text-success" />;
    return <Info className="w-5 h-5 text-primary" />;
  };

  const getBorderColor = (type) => {
    if (type.includes('discrepancy') || type.includes('conflict') || type.includes('overdue')) return 'border-l-error';
    if (type.includes('approve') || type.includes('assigned')) return 'border-l-success';
    return 'border-l-primary';
  };

  const getBgColor = (type) => {
    if (type.includes('discrepancy') || type.includes('conflict') || type.includes('overdue')) return 'bg-error/10';
    if (type.includes('approve') || type.includes('assigned')) return 'bg-success/10';
    return 'bg-primary/10';
  };

  if (loading) return <div className="p-8 text-tertiary">Loading notifications...</div>;

  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-semibold text-secondary">Activity Logs & Notifications</h1>
        <p className="text-tertiary">System alerts and tracking events.</p>
      </div>

      <div className="flex gap-4 border-b border-border pb-2">
        <button className="text-sm font-semibold text-primary border-b-2 border-primary px-2 pb-1">All</button>
      </div>

      <div className="space-y-4">
        {notifications.length === 0 && <Card className="p-8 text-center text-tertiary">No notifications.</Card>}
        
        {notifications.map(notif => (
          <Card key={notif.id} className={`p-4 flex gap-4 items-start border-l-4 ${getBorderColor(notif.type)} ${notif.read ? 'opacity-70' : ''}`}>
            <div className={`p-2 rounded-full shrink-0 ${getBgColor(notif.type)}`}>
              {getIcon(notif.type)}
            </div>
            <div className="flex-1">
              <div className="flex justify-between">
                <h3 className={`font-semibold ${notif.read ? 'text-tertiary' : 'text-secondary'}`}>{notif.type}</h3>
                <span className="text-xs text-tertiary">{new Date(notif.created_at).toLocaleString()}</span>
              </div>
              <p className={`text-sm mt-1 ${notif.read ? 'text-tertiary' : 'text-secondary'}`}>{notif.message}</p>
              {!notif.read && (
                <button onClick={() => handleMarkAsRead(notif.id)} className="mt-3 text-xs font-semibold text-primary flex items-center gap-1 hover:underline">
                  <Check className="w-3 h-3" /> Mark as Read
                </button>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
