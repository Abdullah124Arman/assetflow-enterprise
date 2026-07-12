import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Button from '../../components/ui/Button';

export default function Signup() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      const { api, buildXml } = await import('../../api/client');
      const xmlPayload = buildXml('auth_request', { email, password, name });
      await api.post('/auth/signup', xmlPayload);
      navigate('/login');
    } catch (err) {
      setError(err.message || 'Signup failed.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md p-8 bg-white border border-border rounded-xl shadow-sm">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-primary mb-2">AssetFlow</h1>
          <p className="text-tertiary text-sm">Create your employee account.</p>
        </div>

        <form onSubmit={handleSignup} className="flex flex-col gap-5">
          <div>
            <label className="block text-sm font-semibold mb-1 text-secondary">Full Name</label>
            <input 
              type="text" 
              required
              className="w-full p-2.5 border border-border rounded focus:outline-none focus:border-primary text-sm"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
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

          <p className="text-xs text-tertiary text-center px-4">
            By signing up, you will be assigned the base Employee role. Contact your Admin for promotion.
          </p>

          {error && <p className="text-sm font-medium text-error text-center">{error}</p>}

          <Button type="submit" disabled={isLoading} className="w-full py-2.5 mt-2 text-base">
            {isLoading ? 'Signing Up...' : 'Sign Up'}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-tertiary">
          Already have an account? <Link to="/login" className="text-primary font-medium hover:underline">Log in</Link>
        </p>
      </div>
    </div>
  );
}
