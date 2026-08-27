import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Layers, Mail, ArrowLeft, Send } from 'lucide-react';
import { motion } from 'framer-motion';
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
    <div className="bg-bgGray min-h-screen flex items-center justify-center p-4 antialiased font-sans relative overflow-hidden">
      {/* Background Decorative Blobs */}
      <div className="absolute top-[10%] left-[10%] w-[30%] h-[30%] bg-brand-primary/10 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-[10%] right-[10%] w-[30%] h-[30%] bg-brand-secondary/10 rounded-full blur-[100px] pointer-events-none" />

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
          <h1 className="text-3xl font-black text-slate-800 tracking-tight">Reset Password</h1>
          <p className="text-sm text-slate-500 mt-2 font-medium">Enter your email address and we'll send you a secure reset link.</p>
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
        <form className="space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Email Address</label>
            <div className="relative group">
              <Mail className="w-5 h-5 text-slate-400 absolute left-4 top-3.5 transition-colors group-focus-within:text-brand-primary" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="doctor@hospital.com"
                className="w-full pl-12 pr-4 py-3.5 bg-slate-50 border border-slate-200 focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 rounded-xl text-sm font-medium text-slate-800 outline-none transition-all"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-4 bg-brand-primary hover:bg-stellarDark text-white text-sm font-bold rounded-xl transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0 active:shadow-md disabled:opacity-70 disabled:pointer-events-none flex items-center justify-center space-x-2"
          >
            <Send className="w-4 h-4 mr-1" />
            <span>{isLoading ? 'Sending Link...' : 'Send Reset Link'}</span>
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
