import React, { createContext, useContext, useState, useEffect } from 'react';
import { initialAssets, initialBookings, initialAudit } from '../api/mockData';
import { api, buildXMLPayload } from '../api/client';

const DataContext = createContext(null);

export function DataProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return localStorage.getItem('assetflow_auth') === 'true';
  });

  const login = async (email, password) => {
    try {
      const xmlPayload = buildXMLPayload('auth_request', { email, password });
      const response = await api.post('/auth/login', xmlPayload);
      
      // Extract the access token based on auth_response.xsd schema
      const token = response.response?.data?.auth?.access_token;
      if (token) {
        setIsAuthenticated(true);
        localStorage.setItem('assetflow_auth', 'true');
        localStorage.setItem('assetflow_token', token);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login failed:', error);
      throw error; // Let the UI handle the error display
    }
  };

  const logout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('assetflow_auth');
    localStorage.removeItem('assetflow_token');
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
