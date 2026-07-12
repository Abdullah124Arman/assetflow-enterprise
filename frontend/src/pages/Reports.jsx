import React from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { Download } from 'lucide-react';

export default function Reports() {
  return (
    <div className="flex flex-col gap-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-secondary">Reports & Analytics</h1>
          <p className="text-tertiary">Insights into asset utilization and system health.</p>
        </div>
        <Button className="flex items-center gap-2">
          <Download className="w-4 h-4" /> Export Report
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6 h-64 flex flex-col">
          <h2 className="text-lg font-semibold mb-4">Utilization by Department</h2>
          <div className="flex-1 flex items-end justify-around pb-4">
            <div className="w-12 bg-primary/20 rounded-t h-[80%] relative"><span className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs">ENG</span></div>
            <div className="w-12 bg-primary/40 rounded-t h-[60%] relative"><span className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs">HR</span></div>
            <div className="w-12 bg-primary/60 rounded-t h-[95%] relative"><span className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs">SALES</span></div>
            <div className="w-12 bg-primary rounded-t h-[40%] relative"><span className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs">MKT</span></div>
          </div>
        </Card>
        <Card className="p-6 h-64 flex flex-col">
          <h2 className="text-lg font-semibold mb-4">Maintenance Frequency</h2>
          <div className="flex-1 flex items-center justify-center border-b border-l border-border relative">
            <svg className="w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 100">
              <polyline fill="none" stroke="#2563eb" strokeWidth="2" points="0,80 20,60 40,75 60,30 80,45 100,20" />
            </svg>
            <div className="absolute bottom-1 w-full flex justify-between text-[10px] text-tertiary px-2">
              <span>Jan</span><span>Feb</span><span>Mar</span><span>Apr</span><span>May</span><span>Jun</span>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Most Used Assets</h2>
          <div className="space-y-4">
            <div className="flex justify-between border-b border-border pb-2 text-sm">
              <span className="font-medium text-secondary">Conf Room Projector</span>
              <span className="text-tertiary">40 hrs/wk</span>
            </div>
            <div className="flex justify-between border-b border-border pb-2 text-sm">
              <span className="font-medium text-secondary">MacBook Pro 16"</span>
              <span className="text-tertiary">38 hrs/wk</span>
            </div>
            <div className="flex justify-between border-b border-border pb-2 text-sm">
              <span className="font-medium text-secondary">iPad Pro</span>
              <span className="text-tertiary">25 hrs/wk</span>
            </div>
          </div>
        </Card>
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Assets Due for Maintenance</h2>
          <div className="space-y-4">
            <div className="flex justify-between border-b border-border pb-2 text-sm">
              <span className="font-medium text-secondary">HVAC Unit B</span>
              <span className="text-warning font-semibold">Due in 2 days</span>
            </div>
            <div className="flex justify-between border-b border-border pb-2 text-sm">
              <span className="font-medium text-secondary">Printer 101</span>
              <span className="text-tertiary">Due in 5 days</span>
            </div>
            <div className="flex justify-between border-b border-border pb-2 text-sm">
              <span className="font-medium text-secondary">Server Rack 4</span>
              <span className="text-tertiary">Due in 1 week</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
