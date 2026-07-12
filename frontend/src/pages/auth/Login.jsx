import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useData } from '../../providers/DataProvider';
import Button from '../../components/ui/Button';

export default function Login() {
  const [email, setEmail] = useState('admin@assetflow.com');
  const [password, setPassword] = useState('password');
  const [error, setError] = useState('');
  const { login } = useData();
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    if (login(email, password)) {
      navigate('/dashboard');
    } else {
      setError('Invalid email or password.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md p-8 bg-white border border-border rounded-xl shadow-sm">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-primary mb-2">AssetFlow</h1>
          <p className="text-tertiary text-sm">Sign in to your enterprise account.</p>
        </div>

        <form onSubmit={handleLogin} className="flex flex-col gap-5">
          <div>
            <label className="block text-sm font-semibold mb-1 text-secondary">Email Address</label>
            <input 
              type="email" 
              required
              className="w-full p-2.5 border border-border rounded focus:outline-none focus:border-primary text-sm"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-1 text-secondary">Password</label>
            <input 
              type="password" 
              required
              className="w-full p-2.5 border border-border rounded focus:outline-none focus:border-primary text-sm"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {error && <p className="text-sm font-medium text-error">{error}</p>}

          <Button type="submit" className="w-full py-2.5 mt-2 text-base">Sign In</Button>
        </form>

        <p className="mt-6 text-center text-sm text-tertiary">
          Don't have an account? <Link to="/signup" className="text-primary font-medium hover:underline">Sign up</Link>
        </p>
      </div>
    </div>
  );
}
