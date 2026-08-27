import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Layers, ShieldCheck, Mail, Lock, EyeOff, Eye, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import { api } from '../services/api';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await api.login(email.trim().toLowerCase(), password);
      if (response.user) {
        localStorage.setItem('user', JSON.stringify(response.user));
      }
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Invalid email or password!');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-bgGray min-h-screen flex items-center justify-center p-4 antialiased font-sans relative overflow-hidden">
      {/* Background Decorative Blobs */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-brand-secondary/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-brand-primary/10 rounded-full blur-[120px] pointer-events-none" />

      <motion.div 
        initial={{ opacity: 0, y: 20, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="bg-white rounded-[2rem] shadow-2xl max-w-5xl w-full grid grid-cols-1 md:grid-cols-12 overflow-hidden min-h-[600px] border border-white/50 relative z-10"
      >
        {/* Left Banner */}
        <div className="md:col-span-5 bg-stellarNavy p-10 flex flex-col justify-between text-white relative overflow-hidden">
          {/* Subtle Abstract Background Overlay */}
          <div className="absolute inset-0 bg-gradient-to-br from-brand-secondary/20 to-transparent pointer-events-none" />
          
          <div className="relative z-10 flex items-center space-x-3">
            <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center backdrop-blur-sm border border-white/10">
              <Layers className="w-5 h-5 text-sky-300" />
            </div>
            <span className="text-xl font-bold tracking-wide">StellarX</span>
          </div>
          
          <div className="relative z-10 my-auto space-y-6">
            <motion.h1 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2, duration: 0.5 }}
              className="text-4xl font-black leading-tight tracking-tight"
            >
              Precision AI<br />Skin Diagnostics.
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4, duration: 0.5 }}
              className="text-sm text-sky-100/80 leading-relaxed max-w-sm"
            >
              Empowering healthcare professionals with state-of-the-art diagnostic tools and secure, cloud-based patient analysis.
            </motion.p>
          </div>

          <div className="relative z-10 flex items-center space-x-3 text-xs text-sky-200/80 bg-white/5 p-4 rounded-2xl border border-white/5 backdrop-blur-sm">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <span>Secure access powered by <strong className="text-white">cloud authentication</strong></span>
          </div>
        </div>

        {/* Right Interaction Form */}
        <div className="md:col-span-7 p-10 md:p-16 flex flex-col justify-center space-y-8 bg-white">
          <div>
            <h2 className="text-3xl font-black text-slate-800 tracking-tight">Welcome Back</h2>
            <p className="text-sm text-slate-500 font-medium mt-2">Sign in to your clinician dashboard</p>
          </div>

          <form className="space-y-6" onSubmit={handleLogin}>
            {/* Email Input */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Email Address</label>
              <div className="relative group">
                <Mail className={`w-5 h-5 absolute left-4 top-3.5 transition-colors ${error ? 'text-red-400' : 'text-slate-400 group-focus-within:text-brand-primary'}`} />
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="doctor@hospital.com" 
                  className={`w-full pl-12 pr-4 py-3.5 bg-slate-50 border ${error ? 'border-red-300 ring-4 ring-red-500/10' : 'border-slate-200 focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10'} rounded-xl text-sm font-medium text-slate-800 outline-none transition-all`}
                  required
                />
              </div>
              {error && (
                <motion.p initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }} className="text-xs font-bold text-red-500 mt-1 pl-1">
                  {error}
                </motion.p>
              )}
            </div>

            {/* Password Input */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Password</label>
              <div className="relative group">
                <Lock className="w-5 h-5 absolute left-4 top-3.5 transition-colors text-slate-400 group-focus-within:text-brand-primary" />
                <input 
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••" 
                  className="w-full pl-12 pr-12 py-3.5 bg-slate-50 border border-slate-200 focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 rounded-xl text-sm font-medium text-slate-800 outline-none transition-all"
                  required
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

            {/* Remember / Forgot Block */}
            <div className="flex items-center justify-between text-sm font-semibold">
              <label className="flex items-center space-x-2 cursor-pointer text-slate-600 group">
                <input type="checkbox" className="rounded-md text-brand-primary focus:ring-brand-primary/20 border-slate-300 transition-all cursor-pointer" />
                <span className="group-hover:text-slate-800 transition-colors">Remember me</span>
              </label>
              <Link to="/forgot-password" className="text-brand-primary hover:text-brand-secondary transition-colors">Forgot password?</Link>
            </div>

            {/* Action Button */}
            <button 
              type="submit" 
              disabled={isLoading}
              className="w-full py-4 bg-brand-primary hover:bg-stellarDark text-white text-sm font-bold rounded-xl transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0 active:shadow-md disabled:opacity-70 disabled:pointer-events-none flex items-center justify-center space-x-2 group"
            >
              <span>{isLoading ? 'Authenticating...' : 'Secure Sign In'}</span>
              {!isLoading && <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />}
            </button>
          </form>

          {/* Fixed Register Link */}
          <div className="text-center text-sm text-slate-500 font-semibold pt-4">
            New to StellarX? 
            <Link to="/register" className="text-brand-primary hover:text-brand-secondary ml-1.5 transition-colors">
              Create an account
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
