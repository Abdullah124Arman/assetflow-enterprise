import React, { createContext, useContext, useState, useEffect } from 'react';
import { initialAssets, initialBookings, initialMaintenance, initialAudit } from '../api/mockData';

const DataContext = createContext(null);

export function DataProvider({ children }) {
  const [assets, setAssets] = useState(() => {
    const saved = localStorage.getItem('assetflow_assets');
    return saved ? JSON.parse(saved) : initialAssets;
  });

  const [maintenance, setMaintenance] = useState(() => {
    const saved = localStorage.getItem('assetflow_maintenance');
    return saved ? JSON.parse(saved) : initialMaintenance;
  });

  useEffect(() => {
    localStorage.setItem('assetflow_assets', JSON.stringify(assets));
  }, [assets]);

  useEffect(() => {
    localStorage.setItem('assetflow_maintenance', JSON.stringify(maintenance));
  }, [maintenance]);

  return (
    <DataContext.Provider value={{
      assets, setAssets,
      maintenance, setMaintenance,
      initialBookings,
      initialAudit
    }}>
      {children}
    </DataContext.Provider>
  );
}

export const useData = () => useContext(DataContext);
