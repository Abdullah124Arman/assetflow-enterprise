import React, { createContext, useContext, useState, useEffect } from 'react';
import { initialAssets, initialBookings, initialMaintenance, initialAudit } from '../api/mockData';

const DataContext = createContext(null);

export function DataProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return localStorage.getItem('assetflow_auth') === 'true';
  });

  const login = (email, password) => {
    if (email === 'admin@assetflow.com' && password === 'password') {
      setIsAuthenticated(true);
      localStorage.setItem('assetflow_auth', 'true');
      return true;
    }
    return false;
  };

  const logout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('assetflow_auth');
  };

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
      isAuthenticated,
      login,
      logout,
      assets,
      setAssets,
      maintenance,
      setMaintenance,
      initialBookings,
      initialAudit
    }}>
      {children}
    </DataContext.Provider>
  );
}

export const useData = () => useContext(DataContext);
