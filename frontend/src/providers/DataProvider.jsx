import React, { createContext, useContext, useState, useEffect } from 'react';
import { initialAssets, initialBookings, initialAudit } from '../api/mockData';
import { api } from '../api/client';

const DataContext = createContext(null);

export function DataProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return localStorage.getItem('assetflow_auth') === 'true';
  });

  const [currentUser, setCurrentUser] = useState(() => {
    const token = localStorage.getItem('assetflow_token');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return {
          role: payload.role,
          department_id: payload.department_id,
        };
      } catch (e) {
        return null;
      }
    }
    return null;
  });

  const login = async (email, password) => {
    try {
      const xmlPayload = `<auth_request><email>${email}</email><password>${password}</password></auth_request>`;
      const responseDoc = await api.post('/auth/login', xmlPayload);
      
      // Extract the access token based on auth_response.xsd schema
      const token = responseDoc.querySelector('access_token')?.textContent;
      if (token) {
        setIsAuthenticated(true);
        localStorage.setItem('assetflow_auth', 'true');
        localStorage.setItem('assetflow_token', token);
        
        try {
          const payload = JSON.parse(atob(token.split('.')[1]));
          setCurrentUser({
            role: payload.role,
            department_id: payload.department_id,
          });
        } catch (e) {
          console.error('Failed to parse token payload:', e);
        }

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
    setCurrentUser(null);
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
      currentUser,
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
