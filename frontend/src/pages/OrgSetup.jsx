import React from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';

export default function OrgSetup() {
  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-semibold text-secondary">Organization Setup</h1>
        <p className="text-tertiary">Manage departments, roles, and system settings.</p>
      </div>
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Departments</h2>
        <div className="space-y-4">
          <div className="flex justify-between items-center p-4 border border-border rounded">
            <div>
              <p className="font-medium text-secondary">Engineering</p>
              <p className="text-xs text-tertiary">Head: Sarah Connor</p>
            </div>
            <Button variant="secondary">Edit</Button>
          </div>
          <div className="flex justify-between items-center p-4 border border-border rounded">
            <div>
              <p className="font-medium text-secondary">Marketing</p>
              <p className="text-xs text-tertiary">Head: Don Draper</p>
            </div>
            <Button variant="secondary">Edit</Button>
          </div>
        </div>
        <Button className="mt-4">+ Add Department</Button>
      </Card>
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Roles & Permissions</h2>
        <p className="text-sm text-tertiary mb-4">Users are assigned the 'Employee' role by default upon signup. Promote users below.</p>
        <div className="space-y-4">
          <div className="flex justify-between items-center p-4 border border-border rounded bg-gray-50">
            <div>
              <p className="font-medium text-secondary">Priya Patel</p>
              <p className="text-xs text-tertiary">Current Role: Employee</p>
            </div>
            <select className="p-2 border border-border rounded text-sm bg-white">
              <option>Employee</option>
              <option>Asset Manager</option>
              <option>Department Head</option>
              <option>Admin</option>
            </select>
          </div>
        </div>
      </Card>
    </div>
  );
}
