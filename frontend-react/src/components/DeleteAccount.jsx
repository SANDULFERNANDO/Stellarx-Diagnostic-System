import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Layers, Lock, AlertTriangle } from 'lucide-react';
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
    <div className="bg-bgGray min-h-screen flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-xl max-w-md w-full p-8 space-y-6">
        {/* Header */}
        <div className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Layers className="w-8 h-8 text-stellarNavy" />
            <span className="text-2xl font-black tracking-wide text-stellarNavy">StellarX</span>
          </div>
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertTriangle className="w-8 h-8 text-red-600" />
          </div>
          <h1 className="text-2xl font-black text-red-600">Delete Account</h1>
          <p className="text-sm text-slate-500 mt-1">This action is <strong>permanent</strong> and cannot be undone.</p>
        </div>

        {/* Warning Messages */}
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 space-y-2">
          <p className="text-xs text-red-700 font-bold">⚠️ Deleting your account will:</p>
          <ul className="text-xs text-red-600 list-disc pl-5 space-y-1">
            <li>Permanently remove your account</li>
            <li>Delete all your patient cases</li>
            <li>Remove all uploaded images</li>
            <li>Delete all diagnostic results</li>
            <li>This action is <strong>IRREVERSIBLE</strong></li>
          </ul>
        </div>

        {/* Messages */}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm">
            ✅ {success} Redirecting to login...
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
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Confirm Your Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3.5" />
              <input
                type="password"
                required
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="Enter your password to confirm"
                className="w-full pl-10 pr-4 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-red-500 transition-colors"
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input 
              type="checkbox" 
              id="confirmCheck" 
              required 
              checked={confirmCheck}
              onChange={e => setConfirmCheck(e.target.checked)}
              className="w-4 h-4 text-red-600 border-slate-300 rounded" 
            />
            <label htmlFor="confirmCheck" className="text-xs font-medium text-slate-600">
              I understand that this action is <strong>permanent</strong> and cannot be undone.
            </label>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3.5 bg-red-600 hover:bg-red-700 text-white text-sm font-bold rounded-xl transition-colors shadow-md active:scale-[0.99] disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Deleting...' : 'Permanently Delete Account'}
          </button>
        </form>

        <div className="text-center text-xs text-slate-500 font-medium">
          Changed your mind? <Link to="/profile" className="text-stellarNavy font-bold hover:underline">Back to Profile</Link>
        </div>
      </div>
    </div>
  );
}
