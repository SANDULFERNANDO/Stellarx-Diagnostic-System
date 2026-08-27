import { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Layers, Lock } from 'lucide-react';
import { api } from '../services/api';

export default function ResetPassword() {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const resetToken = searchParams.get('token');

  const reqs = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setSuccess('');
    setError('');

    if (!resetToken) {
      setError('❌ Invalid reset link. Please request a new one.');
      return;
    }
    if (password !== confirmPassword) {
      setError('❌ Passwords do not match.');
      return;
    }
    if (password.length < 8) {
      setError('❌ Password must be at least 8 characters.');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${api.API_BASE_URL || 'http://127.0.0.1:8081'}/auth/reset-password?token=${encodeURIComponent(resetToken)}&new_password=${encodeURIComponent(password)}`, {
        method: 'POST',
      });
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Something went wrong. Please try again.');
      }

      setSuccess('✅ ' + (data.message || 'Password reset successfully!'));
      
      setTimeout(() => {
        navigate('/login');
      }, 3000);
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
          <h1 className="text-2xl font-black text-slate-800">Create New Password</h1>
          <p className="text-sm text-slate-500 mt-1">Enter your new password below.</p>
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
        <form className="space-y-4" onSubmit={handleResetPassword}>
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">New Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3.5" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength="8"
                placeholder="Enter new password"
                className="w-full pl-10 pr-4 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-sky-500 transition-colors"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Confirm Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3.5" />
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength="8"
                placeholder="Confirm new password"
                className="w-full pl-10 pr-4 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-sky-500 transition-colors"
              />
            </div>
          </div>

          {/* Password Requirements */}
          <div className="text-xs text-slate-500 space-y-1">
            <p className="font-bold">Password must contain:</p>
            <ul className="list-disc pl-5 space-y-0.5">
              <li className={reqs.length ? "text-emerald-500" : "text-slate-500"}>At least 8 characters</li>
              <li className={reqs.uppercase ? "text-emerald-500" : "text-slate-500"}>At least one uppercase letter</li>
              <li className={reqs.lowercase ? "text-emerald-500" : "text-slate-500"}>At least one lowercase letter</li>
              <li className={reqs.number ? "text-emerald-500" : "text-slate-500"}>At least one number</li>
              <li className={reqs.special ? "text-emerald-500" : "text-slate-500"}>At least one special character (!@#$%^&*)</li>
            </ul>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3.5 bg-stellarNavy hover:bg-stellarDark text-white text-sm font-bold rounded-xl transition-colors shadow-md active:scale-[0.99] disabled:opacity-70"
          >
            {isLoading ? 'Resetting...' : 'Reset Password'}
          </button>
        </form>

        {/* Back to Login */}
        <div className="text-center text-xs text-slate-500 font-medium">
          <Link to="/login" className="text-stellarNavy font-bold hover:underline cursor-pointer">
            Back to Login
          </Link>
        </div>
      </div>
    </div>
  );
}
