export const initialAssets = [
  { id: 'AF-0012', name: 'Dell XPS 15', category: 'Laptop', status: 'Available', location: 'IT Storage' },
  { id: 'AF-0013', name: 'Herman Miller Chair', category: 'Furniture', status: 'Allocated', location: 'Desk 4B', holder: 'Elena Rodriguez' },
  { id: 'AF-0014', name: 'Conf Room Projector', category: 'AV Eqpt', status: 'Under Maintenance', location: 'Repair Room' },
  { id: 'AF-0015', name: 'iPad Pro', category: 'Tablet', status: 'Lost', location: 'Unknown' },
];

export const initialBookings = [
  { id: 1, resource: 'Meeting Room A', start: '09:00', end: '10:00', status: 'booked', user: 'Procurement Team' },
  { id: 2, resource: 'Meeting Room A', start: '09:30', end: '10:30', status: 'conflict', user: 'Marketing' },
];

export const initialMaintenance = {
  pending: [{ id: 'AF-0018', summary: 'Broken screen', urgency: 'High' }],
  approved: [{ id: 'AF-0012', summary: 'Keyboard sticky', urgency: 'Low' }],
  assigned: [{ id: 'AF-0022', summary: 'Firmware update', urgency: 'Medium', tech: 'Tech Mike' }],
  inProgress: [{ id: 'AF-0005', summary: 'AC servicing', urgency: 'High' }],
  resolved: [{ id: 'AF-0014', summary: 'Lamp replaced', urgency: 'Low' }]
};

export const initialAudit = [
  { id: 'AF-0012', name: 'Dell XPS 15', location: 'IT Storage', verification: 'verified' },
  { id: 'AF-0015', name: 'iPad Pro', location: 'Desk 4B', verification: 'missing' },
];
