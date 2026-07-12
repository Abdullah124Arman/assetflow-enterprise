import React, { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { X } from 'lucide-react';
import { api, buildXml } from '../api/client';

export default function OrgSetup() {
  const [activeTab, setActiveTab] = useState('departments');
  const [departments, setDepartments] = useState([]);
  const [categories, setCategories] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);

  const [showAddDept, setShowAddDept] = useState(false);
  const [newDept, setNewDept] = useState({ name: '', head_id: '', parent_dept_id: '', status: 'active' });
  
  const [showAddCategory, setShowAddCategory] = useState(false);
  const [newCategory, setNewCategory] = useState({ name: '' });

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch all required data
      const [deptDoc, catDoc, empDoc] = await Promise.all([
        api.get('/departments'),
        api.get('/categories'),
        api.get('/employees')
      ]);

      const deptItems = Array.from(deptDoc.querySelectorAll('department, list-item')).map(node => ({
        id: node.querySelector('id')?.textContent,
        name: node.querySelector('name')?.textContent,
        head: node.querySelector('head_name')?.textContent,
        status: node.querySelector('status')?.textContent,
      }));
      setDepartments(deptItems);

      const catItems = Array.from(catDoc.querySelectorAll('category, list-item')).map(node => ({
        id: node.querySelector('id')?.textContent,
        name: node.querySelector('name')?.textContent,
      }));
      setCategories(catItems);

      const empItems = Array.from(empDoc.querySelectorAll('employee, list-item')).map(node => ({
        id: node.querySelector('id')?.textContent,
        name: node.querySelector('name')?.textContent,
        role: node.querySelector('role')?.textContent,
      }));
      setEmployees(empItems);
    } catch (e) {
      console.error("Failed to fetch data", e);
    } finally {
      setLoading(false);
    }
  };

  const updateRole = async (id, role) => {
    try {
      const xml = buildXml('role_update', { role });
      await api.patch(`/employees/${id}/role`, xml);
      fetchData(); // Refresh list
    } catch (e) {
      alert(e.message || "Failed to update role");
    }
  };

  const handleAddDept = async (e) => {
    e.preventDefault();
    try {
      const payload = { name: newDept.name, status: newDept.status };
      if (newDept.head_id) payload.head_id = newDept.head_id;
      if (newDept.parent_dept_id) payload.parent_dept_id = newDept.parent_dept_id;
      
      const xml = buildXml('department', payload);
      await api.post('/departments', xml);
      setShowAddDept(false);
      setNewDept({ name: '', head_id: '', parent_dept_id: '', status: 'active' });
      fetchData();
    } catch (err) {
      alert(err.message || "Failed to add department");
    }
  };

  const handleAddCategory = async (e) => {
    e.preventDefault();
    try {
      const xml = buildXml('category', { name: newCategory.name });
      await api.post('/categories', xml);
      setShowAddCategory(false);
      setNewCategory({ name: '' });
      fetchData();
    } catch (err) {
      alert(err.message || "Failed to add category");
    }
  };

  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-semibold text-secondary">Organization Setup</h1>
        <p className="text-tertiary">Manage departments, roles, and system settings.</p>
      </div>

      <div className="flex space-x-4 border-b border-border">
        {['departments', 'categories', 'employees'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`pb-2 px-1 text-sm font-medium capitalize ${
              activeTab === tab ? 'border-b-2 border-primary text-primary' : 'text-tertiary hover:text-secondary'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {activeTab === 'departments' && (
        <Card className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Departments</h2>
            <Button onClick={() => setShowAddDept(true)}>+ Add Department</Button>
          </div>
          {loading ? <p>Loading...</p> : (
            <div className="space-y-4">
              {departments.map(dept => (
                <div key={dept.id} className="flex justify-between items-center p-4 border border-border rounded">
                  <div>
                    <p className="font-medium text-secondary">{dept.name}</p>
                    <p className="text-xs text-tertiary">Head: {dept.head || 'None'} • Status: {dept.status}</p>
                  </div>
                  <Button variant="secondary">Edit</Button>
                </div>
              ))}
              {departments.length === 0 && <p className="text-sm text-tertiary">No departments found.</p>}
            </div>
          )}
        </Card>
      )}

      {activeTab === 'categories' && (
        <Card className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Categories</h2>
            <Button onClick={() => setShowAddCategory(true)}>+ Add Category</Button>
          </div>
          {loading ? <p>Loading...</p> : (
            <div className="space-y-4">
              {categories.map(cat => (
                <div key={cat.id} className="flex justify-between items-center p-4 border border-border rounded">
                  <p className="font-medium text-secondary">{cat.name}</p>
                  <Button variant="secondary">Edit</Button>
                </div>
              ))}
              {categories.length === 0 && <p className="text-sm text-tertiary">No categories found.</p>}
            </div>
          )}
        </Card>
      )}

      {activeTab === 'employees' && (
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Roles & Permissions</h2>
          <p className="text-sm text-tertiary mb-4">Users are assigned the 'employee' role by default upon signup. Promote users below.</p>
          {loading ? <p>Loading...</p> : (
            <div className="space-y-4">
              {employees.map(emp => (
                <div key={emp.id} className="flex justify-between items-center p-4 border border-border rounded bg-gray-50">
                  <div>
                    <p className="font-medium text-secondary">{emp.name}</p>
                    <p className="text-xs text-tertiary">Current Role: {emp.role}</p>
                  </div>
                  <select
                    className="p-2 border border-border rounded text-sm bg-white"
                    value={emp.role}
                    onChange={(e) => updateRole(emp.id, e.target.value)}
                  >
                    <option value="employee">Employee</option>
                    <option value="asset_manager">Asset Manager</option>
                    <option value="dept_head">Department Head</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
              ))}
              {employees.length === 0 && <p className="text-sm text-tertiary">No employees found.</p>}
            </div>
          )}
        </Card>
      )}

      {showAddDept && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold">Add Department</h2>
              <button onClick={() => setShowAddDept(false)} className="text-tertiary hover:text-secondary">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleAddDept} className="flex flex-col gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Department Name</label>
                <input required type="text" className="w-full p-2 border rounded" value={newDept.name} onChange={e => setNewDept({...newDept, name: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Head (Optional)</label>
                <select className="w-full p-2 border rounded bg-white" value={newDept.head_id} onChange={e => setNewDept({...newDept, head_id: e.target.value})}>
                  <option value="">None</option>
                  {employees.map(emp => (
                    <option key={emp.id} value={emp.id}>{emp.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Parent Department (Optional)</label>
                <select className="w-full p-2 border rounded bg-white" value={newDept.parent_dept_id} onChange={e => setNewDept({...newDept, parent_dept_id: e.target.value})}>
                  <option value="">None</option>
                  {departments.map(dept => (
                    <option key={dept.id} value={dept.id}>{dept.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Status</label>
                <select className="w-full p-2 border rounded" value={newDept.status} onChange={e => setNewDept({...newDept, status: e.target.value})}>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                </select>
              </div>
              <div className="flex justify-end gap-3 mt-4">
                <Button variant="secondary" onClick={() => setShowAddDept(false)} type="button">Cancel</Button>
                <Button type="submit">Add Department</Button>
              </div>
            </form>
          </Card>
        </div>
      )}

      {showAddCategory && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold">Add Category</h2>
              <button onClick={() => setShowAddCategory(false)} className="text-tertiary hover:text-secondary">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleAddCategory} className="flex flex-col gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Category Name</label>
                <input required type="text" className="w-full p-2 border rounded" value={newCategory.name} onChange={e => setNewCategory({...newCategory, name: e.target.value})} />
              </div>
              <div className="flex justify-end gap-3 mt-4">
                <Button variant="secondary" onClick={() => setShowAddCategory(false)} type="button">Cancel</Button>
                <Button type="submit">Add Category</Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
}
