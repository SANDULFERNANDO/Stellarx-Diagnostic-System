import { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Layers, Lock, Eye, EyeOff, CheckCircle2, Circle, ArrowLeft, KeyRound } from 'lucide-react';
import { motion } from 'framer-motion';
import { api } from '../services/api';

export default function ResetPassword() {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
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
  
  const isValid = reqs.length && reqs.uppercase && reqs.lowercase && reqs.number && reqs.special;

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
    if (!isValid) {
      setError('❌ Password does not meet all requirements.');
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
    <div className="bg-bgGray min-h-screen flex items-center justify-center p-4 antialiased font-sans relative overflow-hidden">
      {/* Background Decorative Blobs */}
      <div className="absolute top-[10%] right-[10%] w-[30%] h-[30%] bg-brand-primary/10 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-[10%] left-[10%] w-[30%] h-[30%] bg-brand-secondary/10 rounded-full blur-[100px] pointer-events-none" />

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="bg-white rounded-3xl shadow-2xl max-w-md w-full p-10 space-y-8 relative z-10 border border-slate-100"
      >
        {/* Header */}
        <div className="text-center">
          <div className="flex items-center justify-center space-x-3 mb-6">
            <div className="w-12 h-12 bg-brand-primary/10 rounded-xl flex items-center justify-center">
              <Layers className="w-6 h-6 text-brand-primary" />
            </div>
          </div>
          <h1 className="text-3xl font-black text-slate-800 tracking-tight">New Password</h1>
          <p className="text-sm text-slate-500 mt-2 font-medium">Create a strong password to secure your account.</p>
        </div>

        {/* Success/Error Messages */}
        {success && (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="bg-emerald-50 border border-emerald-200 text-emerald-700 px-4 py-3 rounded-xl text-sm font-medium">
            {success}
          </motion.div>
        )}
        {error && (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm font-medium">
            {error}
          </motion.div>
        )}

        {/* Form */}
        <form className="space-y-6" onSubmit={handleResetPassword}>
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">New Password</label>
            <div className="relative group">
              <Lock className="w-5 h-5 text-slate-400 absolute left-4 top-3.5 transition-colors group-focus-within:text-brand-primary" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="••••••••"
                className="w-full pl-12 pr-12 py-3.5 bg-slate-50 border border-slate-200 focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 rounded-xl text-sm font-medium text-slate-800 outline-none transition-all"
              />
              <button 
                type="button" 
                onClick={() => setShowPassword(!showPassword)} 
                className="absolute right-4 top-3.5 text-slate-400 hover:text-slate-600 transition-colors"
              >
                {showPassword ? <Eye className="w-5 h-5" /> : <EyeOff className="w-5 h-5" />}
              </button>
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Confirm Password</label>
            <div className="relative group">
              <Lock className="w-5 h-5 text-slate-400 absolute left-4 top-3.5 transition-colors group-focus-within:text-brand-primary" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                placeholder="••••••••"
                className="w-full pl-12 pr-4 py-3.5 bg-slate-50 border border-slate-200 focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 rounded-xl text-sm font-medium text-slate-800 outline-none transition-all"
              />
            </div>
          </div>

          {/* Password Requirements Grid */}
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
            <p className="text-xs font-bold text-slate-600 mb-2">Password Requirements</p>
            <div className="grid grid-cols-2 gap-2 text-xs font-medium">
              <div className={`flex items-center space-x-1.5 ${reqs.length ? 'text-emerald-600' : 'text-slate-400'}`}>
                {reqs.length ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Circle className="w-3.5 h-3.5" />}
                <span>8+ characters</span>
              </div>
              <div className={`flex items-center space-x-1.5 ${reqs.uppercase ? 'text-emerald-600' : 'text-slate-400'}`}>
                {reqs.uppercase ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Circle className="w-3.5 h-3.5" />}
                <span>1 uppercase letter</span>
              </div>
              <div className={`flex items-center space-x-1.5 ${reqs.lowercase ? 'text-emerald-600' : 'text-slate-400'}`}>
                {reqs.lowercase ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Circle className="w-3.5 h-3.5" />}
                <span>1 lowercase letter</span>
              </div>
              <div className={`flex items-center space-x-1.5 ${reqs.number ? 'text-emerald-600' : 'text-slate-400'}`}>
                {reqs.number ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Circle className="w-3.5 h-3.5" />}
                <span>1 number</span>
              </div>
              <div className={`flex items-center space-x-1.5 col-span-2 ${reqs.special ? 'text-emerald-600' : 'text-slate-400'}`}>
                {reqs.special ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Circle className="w-3.5 h-3.5" />}
                <span>1 special character (!@#$%^&*)</span>
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={!isValid || isLoading}
            className="w-full py-4 bg-brand-primary hover:bg-stellarDark text-white text-sm font-bold rounded-xl transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0 active:shadow-md disabled:opacity-70 disabled:pointer-events-none flex items-center justify-center space-x-2"
          >
            <KeyRound className="w-4 h-4 mr-1" />
            <span>{isLoading ? 'Resetting...' : 'Reset Password'}</span>
          </button>
        </form>

        {/* Back to Login */}
        <div className="text-center pt-2">
          <Link to="/login" className="inline-flex items-center text-sm font-bold text-slate-500 hover:text-brand-primary transition-colors group">
            <ArrowLeft className="w-4 h-4 mr-1.5 group-hover:-translate-x-1 transition-transform" />
            Back to Sign In
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
