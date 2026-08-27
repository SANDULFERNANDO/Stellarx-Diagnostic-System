import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Layers, Lock, ArrowLeft, ShieldCheck, CheckCircle2, XCircle, KeyRound } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../services/api';

export default function ChangePassword() {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const reqLength = newPassword.length >= 8;
  const reqUppercase = /[A-Z]/.test(newPassword);
  const reqLowercase = /[a-z]/.test(newPassword);
  const reqNumber = /[0-9]/.test(newPassword);
  const reqSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(newPassword);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    if (!reqLength || !reqUppercase || !reqLowercase || !reqNumber || !reqSpecial) {
      setError('Password does not meet all requirements.');
      return;
    }

    if (!api.isAuthenticated()) {
      navigate('/login');
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await api.changePassword(currentPassword, newPassword);
      setSuccess(response.message || 'Password changed successfully!');
      
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      
      setTimeout(() => {
        navigate('/profile');
      }, 2000);
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-bgGray min-h-screen flex items-center justify-center p-4 py-12 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-brand-primary/5 rounded-full blur-[100px] pointer-events-none" />
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-[2rem] shadow-[0_8px_40px_rgb(0,0,0,0.08)] max-w-md w-full p-8 md:p-10 space-y-8 relative z-10 border border-slate-100"
      >
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="w-16 h-16 bg-brand-primary/10 rounded-2xl flex items-center justify-center mx-auto text-brand-primary mb-2">
            <KeyRound className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-800 tracking-tight">Change Password</h1>
            <p className="text-sm font-medium text-slate-500 mt-2 leading-relaxed">
              Ensure your account stays secure by using a strong, unique password.
            </p>
          </div>
        </div>

        {/* Messages */}
        <AnimatePresence mode="wait">
          {success && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }} 
              animate={{ opacity: 1, height: 'auto' }} 
              exit={{ opacity: 0, height: 0 }}
              className="bg-emerald-50 border border-emerald-100 p-4 rounded-xl flex items-start gap-3"
            >
              <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-bold text-emerald-800">Success</p>
                <p className="text-xs font-medium text-emerald-600 mt-1">{success} Redirecting...</p>
              </div>
            </motion.div>
          )}
          
          {error && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }} 
              animate={{ opacity: 1, height: 'auto' }} 
              exit={{ opacity: 0, height: 0 }}
              className="bg-red-50 border border-red-100 p-4 rounded-xl flex items-start gap-3"
            >
              <XCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-bold text-red-800">Error</p>
                <p className="text-xs font-medium text-red-600 mt-1">{error}</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider pl-1">Current Password</label>
            <div className="relative">
              <Lock className="w-5 h-5 text-slate-400 absolute left-4 top-3.5" />
              <input
                type="password"
                required
                value={currentPassword}
                onChange={e => setCurrentPassword(e.target.value)}
                placeholder="Enter current password"
                className="w-full pl-12 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:bg-white focus:outline-none focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 transition-all"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider pl-1">New Password</label>
            <div className="relative">
              <Lock className="w-5 h-5 text-slate-400 absolute left-4 top-3.5" />
              <input
                type="password"
                required
                value={newPassword}
                onChange={e => setNewPassword(e.target.value)}
                placeholder="Enter new password"
                className="w-full pl-12 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:bg-white focus:outline-none focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 transition-all"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider pl-1">Confirm New Password</label>
            <div className="relative">
              <ShieldCheck className="w-5 h-5 text-slate-400 absolute left-4 top-3.5" />
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                placeholder="Confirm new password"
                className="w-full pl-12 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:bg-white focus:outline-none focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 transition-all"
              />
            </div>
          </div>

          <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 space-y-2">
            <p className="text-xs font-bold text-slate-700">Password Requirements:</p>
            <ul className="text-[11px] font-medium space-y-1.5 grid grid-cols-2 gap-x-2">
              <li className={`flex items-center gap-1.5 ${reqLength ? 'text-emerald-600' : 'text-slate-500'}`}>
                <div className={`w-1.5 h-1.5 rounded-full ${reqLength ? 'bg-emerald-500' : 'bg-slate-300'}`} /> 8+ chars
              </li>
              <li className={`flex items-center gap-1.5 ${reqUppercase ? 'text-emerald-600' : 'text-slate-500'}`}>
                <div className={`w-1.5 h-1.5 rounded-full ${reqUppercase ? 'bg-emerald-500' : 'bg-slate-300'}`} /> Uppercase
              </li>
              <li className={`flex items-center gap-1.5 ${reqLowercase ? 'text-emerald-600' : 'text-slate-500'}`}>
                <div className={`w-1.5 h-1.5 rounded-full ${reqLowercase ? 'bg-emerald-500' : 'bg-slate-300'}`} /> Lowercase
              </li>
              <li className={`flex items-center gap-1.5 ${reqNumber ? 'text-emerald-600' : 'text-slate-500'}`}>
                <div className={`w-1.5 h-1.5 rounded-full ${reqNumber ? 'bg-emerald-500' : 'bg-slate-300'}`} /> Number
              </li>
              <li className={`flex items-center gap-1.5 ${reqSpecial ? 'text-emerald-600' : 'text-slate-500'} col-span-2 mt-1`}>
                <div className={`w-1.5 h-1.5 rounded-full ${reqSpecial ? 'bg-emerald-500' : 'bg-slate-300'}`} /> Special character (!@#$...)
              </li>
            </ul>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-4 bg-brand-primary hover:bg-stellarDark text-white text-sm font-bold rounded-xl transition-all shadow-md hover:shadow-lg active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed disabled:hover:scale-100 mt-2"
          >
            {isSubmitting ? (
              <span className="flex items-center justify-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Updating...
              </span>
            ) : 'Update Password'}
          </button>
        </form>

        <div className="text-center pt-2 border-t border-slate-100">
          <Link to="/profile" className="inline-flex items-center gap-1.5 text-sm font-bold text-slate-500 hover:text-brand-primary transition-colors">
            <ArrowLeft className="w-4 h-4" /> Back to Profile
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
