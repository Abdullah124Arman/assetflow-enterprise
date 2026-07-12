import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DataProvider } from './providers/DataProvider';
import DashboardLayout from './components/layout/DashboardLayout';
import Dashboard from './pages/Dashboard';
import AssetDirectory from './pages/AssetDirectory';
import Allocation from './pages/Allocation';

const ComingSoon = ({ title }) => (
  <div className="flex flex-col items-center justify-center h-full text-center">
    <h2 className="text-2xl font-semibold mb-2">{title}</h2>
    <p className="text-tertiary">This screen will be built in an upcoming phase.</p>
  </div>
);

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
            <Route path="org-setup" element={<ComingSoon title="Organization Setup" />} />
            <Route path="booking" element={<ComingSoon title="Resource Booking" />} />
            <Route path="maintenance" element={<ComingSoon title="Maintenance Management" />} />
            <Route path="audit" element={<ComingSoon title="Asset Audit" />} />
            <Route path="reports" element={<ComingSoon title="Reports & Analytics" />} />
            <Route path="notifications" element={<ComingSoon title="Activity Logs & Notifications" />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </DataProvider>
  );
}

export default App;
