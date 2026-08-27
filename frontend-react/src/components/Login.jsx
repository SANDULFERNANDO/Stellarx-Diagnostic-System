import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Layers, ShieldCheck, Mail, Lock, EyeOff, Eye } from 'lucide-react';
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
    <div className="bg-bgGray min-h-screen flex items-center justify-center p-4 antialiased font-sans">
      <div className="bg-white rounded-3xl shadow-xl max-w-5xl w-full grid grid-cols-1 md:grid-cols-12 overflow-hidden min-h-[600px]">
        {/* Left Banner */}
        <div className="md:col-span-5 bg-stellarNavy p-10 flex flex-col justify-between text-white relative">
          <div className="flex items-center space-x-2">
            <Layers className="w-6 h-6 text-white" />
            <span className="text-xl font-bold tracking-wide">StellarX</span>
          </div>
          
          <div className="my-auto space-y-4">
            <h1 className="text-3xl font-black leading-tight">Precision AI<br />Skin Diagnostics.</h1>
            <p className="text-sm text-slate-300 leading-relaxed">Empowering healthcare professionals with state-of-the-art diagnostic tools and secure, cloud-based patient analysis.</p>
          </div>

          <div className="flex items-center space-x-2 text-xs text-slate-300">
            <ShieldCheck className="w-5 h-5" />
            <span>Secure access powered by <strong className="text-white">cloud authentication</strong></span>
          </div>
        </div>

        {/* Right Interaction Form */}
        <div className="md:col-span-7 p-12 flex flex-col justify-center space-y-8">
          <div>
            <h2 className="text-3xl font-black text-slate-800 tracking-tight">Diagnostic System</h2>
            <p className="text-xs text-slate-400 font-medium mt-1">AI-Assisted Clinical Skin Analysis for Healthcare Professionals</p>
          </div>

          <form className="space-y-5" onSubmit={handleLogin}>
            {/* Email Input */}
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Email Address</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3.5" />
                <input 
                  type="text" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@hospital.com" 
                  className={`w-full pl-10 pr-4 py-3 bg-white border ${error ? 'border-red-400' : 'border-slate-200'} rounded-xl text-sm focus:outline-none focus:border-sky-500 transition-colors`}
                  required
                />
              </div>
              {error && <p className="text-xs text-red-500 mt-1">{error}</p>}
            </div>

            {/* Password Input */}
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3.5" />
                <input 
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Password" 
                  className="w-full pl-10 pr-10 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-sky-500 transition-colors"
                  required
                />
                <button 
                  type="button" 
                  onClick={() => setShowPassword(!showPassword)} 
                  className="absolute right-3 top-3.5 text-slate-400 hover:text-slate-600"
                >
                  {showPassword ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Remember / Forgot Block */}
            <div className="flex items-center justify-between text-xs font-medium">
              <label className="flex items-center space-x-2 cursor-pointer text-slate-600">
                <input type="checkbox" className="rounded text-[#114a72] focus:ring-0 border-slate-300" />
                <span>Remember me</span>
              </label>
              <Link to="/forgot-password" className="text-[#114a72] hover:underline font-bold">Forgot password?</Link>
            </div>

            {/* Action Button */}
            <button 
              type="submit" 
              disabled={isLoading}
              className="w-full py-3.5 bg-[#114a72] hover:bg-[#0c3d5e] text-white text-sm font-bold rounded-xl transition-colors shadow-md active:scale-[0.99] disabled:opacity-70"
            >
              {isLoading ? 'Signing In...' : 'Sign In'}
            </button>
          </form>

          {/* Fixed Register Link */}
          <div className="text-center text-xs text-slate-500 font-bold">
            Don't have an account? 
            <Link to="/register" className="text-[#114a72] hover:underline cursor-pointer ml-1 inline-block">
              Register
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
