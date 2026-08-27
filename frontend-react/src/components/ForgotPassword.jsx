import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Layers, Mail } from 'lucide-react';
import { api } from '../services/api';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSuccess('');
    setError('');
    setIsLoading(true);

    try {
      // Assuming apiRequest function logic handles this route correctly:
      const response = await fetch(`${api.API_BASE_URL || 'http://127.0.0.1:8081'}/auth/forgot-password?email=${encodeURIComponent(email.trim().toLowerCase())}`, {
        method: 'POST',
      });
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Something went wrong. Please try again.');
      }
      
      setSuccess('✅ ' + (data.message || 'Password reset link sent!'));
      setEmail('');
    } catch (err) {
      setError('❌ ' + (err.message || 'Something went wrong. Please try again.'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-bgGray min-h-screen flex items-center justify-center p-4 antialiased font-sans">
      <div className="bg-white rounded-3xl shadow-xl max-w-md w-full p-8 space-y-6">
        {/* Header */}
        <div className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Layers className="w-8 h-8 text-stellarNavy" />
            <span className="text-2xl font-black tracking-wide text-stellarNavy">StellarX</span>
          </div>
          <h1 className="text-2xl font-black text-slate-800">Reset Password</h1>
          <p className="text-sm text-slate-500 mt-1">Enter your email address and we'll send you a reset link.</p>
        </div>

        {/* Success/Error Messages */}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm">
            {success}
          </div>
        )}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* Form */}
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3.5" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="name@hospital.com"
                className="w-full pl-10 pr-4 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-sky-500 transition-colors"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3.5 bg-stellarNavy hover:bg-stellarDark text-white text-sm font-bold rounded-xl transition-colors shadow-md active:scale-[0.99] disabled:opacity-70"
          >
            {isLoading ? 'Sending...' : 'Send Reset Link'}
          </button>
        </form>

        {/* Back to Login */}
        <div className="text-center text-xs text-slate-500 font-medium">
          Remember your password?{' '}
          <Link to="/login" className="text-stellarNavy font-bold hover:underline cursor-pointer">
            Back to Login
          </Link>
        </div>
      </div>
    </div>
  );
}
