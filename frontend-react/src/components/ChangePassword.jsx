import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Layers, Lock } from 'lucide-react';
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
    <div className="bg-bgGray min-h-screen flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-xl max-w-md w-full p-8 space-y-6">
        {/* Header */}
        <div className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Layers className="w-8 h-8 text-stellarNavy" />
            <span className="text-2xl font-black tracking-wide text-stellarNavy">StellarX</span>
          </div>
          <h1 className="text-2xl font-black text-slate-800">Change Password</h1>
          <p className="text-sm text-slate-500 mt-1">Enter your current password and set a new one.</p>
        </div>

        {/* Messages */}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm">
            ✅ {success} Redirecting to profile...
          </div>
        )}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
            ❌ {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Current Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3.5" />
              <input
                type="password"
                required
                value={currentPassword}
                onChange={e => setCurrentPassword(e.target.value)}
                placeholder="Enter current password"
                className="w-full pl-10 pr-4 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-sky-500 transition-colors"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">New Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3.5" />
              <input
                type="password"
                required
                value={newPassword}
                onChange={e => setNewPassword(e.target.value)}
                placeholder="Enter new password"
                className="w-full pl-10 pr-4 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-sky-500 transition-colors"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Confirm New Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3.5" />
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                placeholder="Confirm new password"
                className="w-full pl-10 pr-4 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-sky-500 transition-colors"
              />
            </div>
          </div>

          <div className="text-xs text-slate-500 space-y-1">
            <p className="font-bold">Password must contain:</p>
            <ul className="list-disc pl-5 space-y-0.5">
              <li className={reqLength ? 'text-green-500' : 'text-slate-500'}>At least 8 characters</li>
              <li className={reqUppercase ? 'text-green-500' : 'text-slate-500'}>At least one uppercase letter</li>
              <li className={reqLowercase ? 'text-green-500' : 'text-slate-500'}>At least one lowercase letter</li>
              <li className={reqNumber ? 'text-green-500' : 'text-slate-500'}>At least one number</li>
              <li className={reqSpecial ? 'text-green-500' : 'text-slate-500'}>At least one special character (!@#$%^&*)</li>
            </ul>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3.5 bg-stellarNavy hover:bg-stellarDark text-white text-sm font-bold rounded-xl transition-colors shadow-md active:scale-[0.99] disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Changing...' : 'Change Password'}
          </button>
        </form>

        <div className="text-center text-xs text-slate-500 font-medium">
          <Link to="/profile" className="text-stellarNavy font-bold hover:underline">
            Back to Profile
          </Link>
        </div>
      </div>
    </div>
  );
}
