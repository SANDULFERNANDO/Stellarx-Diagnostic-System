import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Layers, ShieldCheck, Mail, Lock, EyeOff, Eye, User, CheckCircle2, Circle } from 'lucide-react';
import { motion } from 'framer-motion';
import { api } from '../services/api';

export default function Register() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isValid, setIsValid] = useState(false);
  const navigate = useNavigate();

  const reqs = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
  };

  useEffect(() => {
    setIsValid(reqs.length && reqs.uppercase && reqs.lowercase && reqs.number && reqs.special);
  }, [password]);

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!isValid) return;
    
    setError('');
    setIsLoading(true);

    const nameParts = name.trim().split(' ');
    const firstName = nameParts[0] || '';
    const lastName = nameParts.slice(1).join(' ') || '';
    const username = email.trim().toLowerCase().split('@')[0];

    try {
      const response = await api.register(username, firstName, lastName, email.trim().toLowerCase(), null, password);
      localStorage.setItem('user', JSON.stringify(response));
      navigate('/login');
    } catch (err) {
      setError(err.message || 'Registration failed!');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-bgGray min-h-screen flex items-center justify-center p-4 antialiased font-sans relative overflow-hidden">
      {/* Background Decorative Blobs */}
      <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-brand-secondary/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-brand-primary/10 rounded-full blur-[120px] pointer-events-none" />

      <motion.div 
        initial={{ opacity: 0, y: 20, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="bg-white rounded-[2rem] shadow-2xl max-w-5xl w-full grid grid-cols-1 md:grid-cols-12 overflow-hidden min-h-[600px] border border-white/50 relative z-10"
      >
        {/* Left Panel Banner */}
        <div className="md:col-span-5 bg-stellarNavy p-10 flex flex-col justify-between text-white relative overflow-hidden">
          {/* Subtle Abstract Background Overlay */}
          <div className="absolute inset-0 bg-gradient-to-tr from-brand-secondary/20 to-transparent pointer-events-none" />
          
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
              Join the AI<br />Clinical Network.
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4, duration: 0.5 }}
              className="text-sm text-sky-100/80 leading-relaxed max-w-sm"
            >
              Create an account to gain full access to state-of-the-art diagnostics, cloud patient portfolios, and secure collaboration tools.
            </motion.p>
          </div>

          <div className="relative z-10 flex items-center space-x-3 text-xs text-sky-200/80 bg-white/5 p-4 rounded-2xl border border-white/5 backdrop-blur-sm">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <span>Secure registry powered by <strong className="text-white">cloud authentication</strong></span>
          </div>
        </div>

        {/* Right Register Options */}
        <div className="md:col-span-7 p-10 md:p-12 flex flex-col justify-center bg-white relative z-10">
          <div className="mb-8">
            <h2 className="text-3xl font-black text-slate-800 tracking-tight">Create Account</h2>
            <p className="text-sm text-slate-500 font-medium mt-2">Register as a healthcare practitioner to begin clinical diagnostic submissions.</p>
          </div>

          <form className="space-y-5" onSubmit={handleRegister}>
            {/* Name */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Full Name</label>
              <div className="relative group">
                <User className="w-5 h-5 absolute left-4 top-3.5 transition-colors text-slate-400 group-focus-within:text-brand-primary" />
                <input 
                  type="text" 
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required 
                  placeholder="John Smith, MD" 
                  className="w-full pl-12 pr-4 py-3.5 bg-slate-50 border border-slate-200 focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 rounded-xl text-sm font-medium text-slate-800 outline-none transition-all"
                />
              </div>
            </div>

            {/* Email */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Email Address</label>
              <div className="relative group">
                <Mail className={`w-5 h-5 absolute left-4 top-3.5 transition-colors ${error ? 'text-red-400' : 'text-slate-400 group-focus-within:text-brand-primary'}`} />
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required 
                  placeholder="name@hospital.com" 
                  className={`w-full pl-12 pr-4 py-3.5 bg-slate-50 border ${error ? 'border-red-300 ring-4 ring-red-500/10' : 'border-slate-200 focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10'} rounded-xl text-sm font-medium text-slate-800 outline-none transition-all`}
                />
              </div>
              {error && (
                <motion.p initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }} className="text-xs font-bold text-red-500 mt-1 pl-1">
                  {error}
                </motion.p>
              )}
            </div>

            {/* Password */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Password</label>
              <div className="relative group">
                <Lock className="w-5 h-5 absolute left-4 top-3.5 transition-colors text-slate-400 group-focus-within:text-brand-primary" />
                <input 
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required 
                  placeholder="Create a strong password" 
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
              
              {/* Password Requirements Grid */}
              <div className="mt-3 bg-slate-50 rounded-xl p-4 border border-slate-100">
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
            </div>

            {/* Legal Terms Checkbox */}
            <label className="flex items-start space-x-3 text-xs font-medium text-slate-500 cursor-pointer pt-2 group">
              <input type="checkbox" required className="mt-0.5 rounded-sm text-brand-primary focus:ring-brand-primary/20 border-slate-300 transition-colors" />
              <span className="leading-relaxed group-hover:text-slate-700 transition-colors">
                I agree to the <a href="#" className="text-brand-primary font-bold hover:text-brand-secondary">Terms of Service</a> and confirm compliance with institutional data processing standards.
              </span>
            </label>

            {/* Submit Button */}
            <button 
              type="submit" 
              disabled={!isValid || isLoading}
              className="w-full py-4 bg-brand-primary hover:bg-stellarDark text-white text-sm font-bold rounded-xl transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0 active:shadow-md disabled:opacity-60 disabled:pointer-events-none mt-2"
            >
              {isLoading ? 'Registering...' : 'Complete Registration'}
            </button>
          </form>

          {/* Sign In Back Link */}
          <div className="text-center text-sm text-slate-500 font-semibold pt-6">
            Already have an account? 
            <Link to="/login" className="text-brand-primary hover:text-brand-secondary ml-1.5 transition-colors">
              Sign In
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
