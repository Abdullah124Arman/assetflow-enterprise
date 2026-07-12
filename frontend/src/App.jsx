import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DataProvider } from './providers/DataProvider';
import DashboardLayout from './components/layout/DashboardLayout';
import Dashboard from './pages/Dashboard';
import AssetDirectory from './pages/AssetDirectory';
import Allocation from './pages/Allocation';

import OrgSetup from './pages/OrgSetup';
import Booking from './pages/Booking';
import Maintenance from './pages/Maintenance';
import Audit from './pages/Audit';
import Reports from './pages/Reports';
import Notifications from './pages/Notifications';

function App() {
  return (
    <DataProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<DashboardLayout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="assets" element={<AssetDirectory />} />
            <Route path="allocation" element={<Allocation />} />
            <Route path="org-setup" element={<OrgSetup />} />
            <Route path="booking" element={<Booking />} />
            <Route path="maintenance" element={<Maintenance />} />
            <Route path="audit" element={<Audit />} />
            <Route path="reports" element={<Reports />} />
            <Route path="notifications" element={<Notifications />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </DataProvider>
  );
}

export default App;
