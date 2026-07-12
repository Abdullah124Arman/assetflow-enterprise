import React from 'react';

export default function StatusChip({ status }) {
  const getStatusStyles = (status) => {
    switch (status.toLowerCase()) {
      case 'available':
      case 'verified':
        return 'bg-success/10 text-success';
      case 'allocated':
      case 'booked':
        return 'bg-primary/10 text-primary';
      case 'under maintenance':
      case 'conflict':
        return 'bg-warning/10 text-warning';
      case 'lost':
      case 'missing':
      case 'damaged':
        return 'bg-error/10 text-error';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider ${getStatusStyles(status)}`}>
      {status}
    </span>
  );
}
