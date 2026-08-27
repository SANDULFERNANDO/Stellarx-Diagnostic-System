import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Layers, Lock, AlertTriangle, ArrowLeft, CheckCircle2, XCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../services/api';

export default function DeleteAccount() {
  const [password, setPassword] = useState('');
  const [confirmCheck, setConfirmCheck] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!confirmCheck) {
      setError('Please confirm that you understand this action is permanent.');
      return;
    }

    if (!api.isAuthenticated()) {
      navigate('/login');
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await api.deleteProfile(password);
      setSuccess(response?.message || 'Account deleted successfully!');
      
      localStorage.clear();
      
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-bgGray min-h-screen flex items-center justify-center p-4 py-12 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-red-500/5 rounded-full blur-[100px] pointer-events-none" />
      
      <motion.div 
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.3, ease: "easeOut" }}
        className="bg-white rounded-[2rem] shadow-[0_8px_40px_rgb(0,0,0,0.08)] max-w-md w-full p-8 md:p-10 space-y-8 relative z-10 border border-slate-100 overflow-hidden"
      >
        <div className="absolute top-0 left-0 w-full h-1.5 bg-red-500" />
        
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="w-20 h-20 bg-red-50 rounded-2xl flex items-center justify-center mx-auto text-red-500 mb-2 relative">
            <div className="absolute inset-0 bg-red-500/10 rounded-2xl animate-pulse" />
            <AlertTriangle className="w-10 h-10 relative z-10" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-800 tracking-tight">Delete Account</h1>
            <p className="text-sm font-medium text-slate-500 mt-2 leading-relaxed">
              This action is <strong className="text-red-500">permanent</strong> and cannot be undone.
            </p>
          </div>
        </div>

        {/* Warning Messages */}
        <div className="bg-red-50/50 border border-red-100 rounded-2xl p-5 space-y-3">
          <p className="text-xs text-red-800 font-bold uppercase tracking-wider flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5" /> Deleting your account will:
          </p>
          <ul className="text-xs text-red-700 font-medium space-y-2 grid grid-cols-1 md:grid-cols-2">
            <li className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-red-400" /> Remove your profile</li>
            <li className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-red-400" /> Delete patient cases</li>
            <li className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-red-400" /> Remove all images</li>
            <li className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-red-400" /> Delete diagnostics</li>
          </ul>
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
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider pl-1">Confirm Your Password</label>
            <div className="relative">
              <Lock className="w-5 h-5 text-slate-400 absolute left-4 top-3.5" />
              <input
                type="password"
                required
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="Enter your password to confirm"
                className="w-full pl-12 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:bg-white focus:outline-none focus:border-red-500 focus:ring-4 focus:ring-red-500/10 transition-all"
              />
            </div>
          </div>

          <div className="flex items-start gap-3 bg-slate-50 p-4 rounded-xl border border-slate-200 cursor-pointer hover:bg-slate-100 transition-colors" onClick={() => setConfirmCheck(!confirmCheck)}>
            <div className="relative flex items-center pt-0.5">
              <input 
                type="checkbox" 
                id="confirmCheck" 
                required 
                checked={confirmCheck}
                onChange={e => setConfirmCheck(e.target.checked)}
                className="w-4 h-4 text-red-600 border-slate-300 rounded cursor-pointer accent-red-600" 
              />
            </div>
            <label htmlFor="confirmCheck" className="text-[11px] font-medium text-slate-600 cursor-pointer leading-relaxed">
              I understand that this action is <strong className="text-red-500">permanent</strong> and cannot be undone under any circumstances.
            </label>
          </div>

          <button
            type="submit"
            disabled={isSubmitting || !confirmCheck}
            className="w-full py-4 bg-red-600 hover:bg-red-700 text-white text-sm font-bold rounded-xl transition-all shadow-md hover:shadow-lg hover:shadow-red-500/20 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 mt-2"
          >
            {isSubmitting ? (
              <span className="flex items-center justify-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Deleting...
              </span>
            ) : 'Permanently Delete Account'}
          </button>
        </form>

        <div className="text-center pt-2 border-t border-slate-100">
          <Link to="/profile" className="inline-flex items-center gap-1.5 text-sm font-bold text-slate-500 hover:text-brand-primary transition-colors">
            <ArrowLeft className="w-4 h-4" /> Cancel and return to Profile
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
