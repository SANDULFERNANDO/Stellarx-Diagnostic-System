import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Layers, ShieldCheck, Mail, Lock, EyeOff, Eye, User } from 'lucide-react';
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
      alert('Registration successful!');
      navigate('/login');
    } catch (err) {
      setError(err.message || 'Registration failed!');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-bgGray min-h-screen flex items-center justify-center p-4 antialiased font-sans">
      <div className="bg-white rounded-3xl shadow-xl max-w-5xl w-full grid grid-cols-1 md:grid-cols-12 overflow-hidden min-h-[600px]">
        {/* Left Panel Banner */}
        <div className="md:col-span-5 bg-stellarNavy p-10 flex flex-col justify-between text-white">
          <div className="flex items-center space-x-2">
            <Layers className="w-6 h-6 text-white" />
            <span className="text-xl font-bold tracking-wide">StellarX</span>
          </div>
          
          <div className="my-auto space-y-4">
            <h1 className="text-3xl font-black leading-tight">Join the AI<br />Clinical Network.</h1>
            <p className="text-sm text-slate-300 leading-relaxed">Create an account to gain full access to state-of-the-art diagnostics, cloud patient portfolios, and secure collaboration tools.</p>
          </div>

          <div className="flex items-center space-x-2 text-xs text-slate-300">
            <ShieldCheck className="w-5 h-5" />
            <span>Secure registry powered by <strong className="text-white">cloud authentication</strong></span>
          </div>
        </div>

        {/* Right Register Options */}
        <div className="md:col-span-7 p-12 flex flex-col justify-center space-y-6">
          <div>
            <h2 className="text-3xl font-black text-slate-800 tracking-tight">Create Account</h2>
            <p className="text-xs text-slate-400 font-medium mt-1">Register as a healthcare practitioner to begin clinical diagnostic submissions.</p>
          </div>

          <form className="space-y-4" onSubmit={handleRegister}>
            {/* Name */}
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Full Name</label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3 top-3.5" />
                <input 
                  type="text" 
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required 
                  placeholder="John Smith" 
                  className="w-full pl-10 pr-4 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-sky-500"
                />
              </div>
            </div>

            {/* Email */}
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
                  className={`w-full pl-10 pr-4 py-3 bg-white border ${error ? 'border-red-400' : 'border-slate-200'} rounded-xl text-sm focus:outline-none focus:border-sky-500`}
                />
              </div>
              {error && <p className="text-xs text-red-500 mt-1">{error}</p>}
            </div>

            {/* Password */}
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3.5" />
                <input 
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required 
                  placeholder="Create a safe password" 
                  className="w-full pl-10 pr-10 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-sky-500"
                />
                <button 
                  type="button" 
                  onClick={() => setShowPassword(!showPassword)} 
                  className="absolute right-3 top-3.5 text-slate-400 hover:text-slate-600"
                >
                  {showPassword ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                </button>
              </div>
              
              {/* Password Requirements */}
              <div className="mt-2 text-xs text-slate-500 space-y-1">
                <p className="font-bold">Password must contain:</p>
                <ul className="list-disc pl-5 space-y-0.5">
                  <li className={reqs.length ? "text-emerald-500" : "text-slate-500"}>At least 8 characters</li>
                  <li className={reqs.uppercase ? "text-emerald-500" : "text-slate-500"}>At least one uppercase letter</li>
                  <li className={reqs.lowercase ? "text-emerald-500" : "text-slate-500"}>At least one lowercase letter</li>
                  <li className={reqs.number ? "text-emerald-500" : "text-slate-500"}>At least one number</li>
                  <li className={reqs.special ? "text-emerald-500" : "text-slate-500"}>At least one special character (!@#$%^&*)</li>
                </ul>
              </div>
            </div>

            {/* Legal Terms Checkbox */}
            <label className="flex items-start space-x-2 text-xs text-slate-500 cursor-pointer pt-2">
              <input type="checkbox" required className="mt-0.5 rounded text-[#114a72] border-slate-300" />
              <span className="leading-normal">I agree to the <a href="#" className="text-[#114a72] font-bold hover:underline">Terms of Service</a> and confirm compliance with institutional data processing standards.</span>
            </label>

            {/* Submit Button */}
            <button 
              type="submit" 
              disabled={!isValid || isLoading}
              className="w-full py-3.5 bg-[#114a72] hover:bg-[#0c3d5e] text-white text-sm font-bold rounded-xl transition-colors shadow-md mt-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Registering...' : 'Register Account'}
            </button>
          </form>

          {/* Sign In Back Link */}
          <div className="text-center text-xs text-slate-500 font-medium">
            Already have an account? 
            <Link to="/login" className="text-[#114a72] font-bold hover:underline cursor-pointer ml-1 inline-block">
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
