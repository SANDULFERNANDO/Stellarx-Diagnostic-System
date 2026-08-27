import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { User, Edit3, Key, Trash2 } from 'lucide-react';
import { api } from '../services/api';

export default function Profile() {
  const [user, setUser] = useState(null);
  const [isEditMode, setIsEditMode] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    position: '',
    phone: '',
    email: ''
  });
  const navigate = useNavigate();

  useEffect(() => {
    if (!api.isAuthenticated()) {
      navigate('/login');
      return;
    }

    const loadUser = async () => {
      let currentUser = api.getUser();
      if (!currentUser) {
        try {
          currentUser = await api.getCurrentUser();
          localStorage.setItem('user', JSON.stringify(currentUser));
          localStorage.setItem('current_user', JSON.stringify(currentUser));
        } catch (err) {
          navigate('/login');
          return;
        }
      }
      setUser(currentUser);
      setFormData({
        name: currentUser.first_name || currentUser.name || currentUser.username || 'Medical Professional',
        position: currentUser.position || 'Healthcare Practitioner',
        phone: currentUser.phone || '+94 77 123 4567',
        email: currentUser.email || ''
      });
    };

    loadUser();
  }, [navigate]);

  const toggleEditMode = () => {
    if (isEditMode) {
      // Cancel edit mode
      setFormData({
        name: user?.first_name || user?.name || user?.username || 'Medical Professional',
        position: user?.position || 'Healthcare Practitioner',
        phone: user?.phone || '+94 77 123 4567',
        email: user?.email || ''
      });
    }
    setIsEditMode(!isEditMode);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSave = (e) => {
    e.preventDefault();
    
    // In a real app, make an API call here.
    // For now, update local storage to match the old logic
    const updatedUser = {
      ...user,
      name: formData.name,
      first_name: formData.name,
      position: formData.position,
      phone: formData.phone
    };

    let usersList = JSON.parse(localStorage.getItem('stellarX_users_list') || '[]');
    usersList = usersList.map(u => u.email === user.email ? { ...u, name: formData.name, position: formData.position, phone: formData.phone } : u);
    
    localStorage.setItem('stellarX_users_list', JSON.stringify(usersList));
    localStorage.setItem('stellarX_current_user', JSON.stringify(updatedUser));
    localStorage.setItem('user', JSON.stringify(updatedUser));
    localStorage.setItem('current_user', JSON.stringify(updatedUser));

    setUser(updatedUser);
    setIsEditMode(false);
    alert('Profile updated successfully!');
  };

  if (!user) {
    return (
      <div className="p-6 md:p-10 max-w-4xl mx-auto w-full flex items-center justify-center">
        <div className="animate-pulse text-slate-400 font-medium">Loading profile...</div>
      </div>
    );
  }

  const displayName = formData.name;
  const displayPosition = formData.position;

  return (
    <div className="p-6 md:p-10 max-w-4xl mx-auto w-full space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-black text-slate-800 tracking-tight">User Profile</h1>
          <p className="text-xs text-slate-400 font-medium mt-1">Manage your practitioner credentials and account details.</p>
        </div>
      </div>

      <div className="bg-white rounded-3xl shadow-xl border border-slate-100 p-8 space-y-8">
        
        {/* Top Profile Overview Layer */}
        <div className="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-6 pb-6 border-b border-slate-100">
          <div className="w-24 h-24 bg-slate-100 rounded-2xl flex items-center justify-center text-stellarNavy border border-slate-200 shadow-inner">
            <User className="w-12 h-12" />
          </div>
          <div className="text-center sm:text-left flex-1">
            <h2 className="text-2xl font-black text-slate-800">{displayName}</h2>
            <p className="text-sm font-bold text-stellarNavy mt-0.5">{displayPosition}</p>
            <p className="text-xs text-slate-400 font-medium mt-1">
              System Account Status: <span className="text-emerald-500 font-bold uppercase">Active</span>
            </p>
          </div>
          <div>
            <button 
              onClick={toggleEditMode} 
              className="px-5 py-2.5 bg-stellarNavy hover:bg-stellarDark text-white text-xs font-bold rounded-xl transition-colors shadow-md flex items-center space-x-2"
            >
              <Edit3 className="w-3.5 h-3.5" />
              <span>{isEditMode ? 'Viewing Mode' : 'Edit Profile'}</span>
            </button>
          </div>
        </div>

        {/* Detail Input Fields Grid Form */}
        <form onSubmit={handleSave} className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Full Name</label>
            <input 
              type="text" 
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              disabled={!isEditMode} 
              required
              className={`w-full px-4 py-3 border border-slate-200 rounded-xl text-sm text-slate-800 focus:outline-none focus:border-sky-500 disabled:opacity-75 transition-colors ${isEditMode ? 'bg-white' : 'bg-slate-50'}`}
            />
          </div>
          
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Position / Title</label>
            <input 
              type="text" 
              name="position"
              value={formData.position}
              onChange={handleInputChange}
              disabled={!isEditMode} 
              required 
              placeholder="e.g. Dermatologist / Medical Student"
              className={`w-full px-4 py-3 border border-slate-200 rounded-xl text-sm text-slate-800 focus:outline-none focus:border-sky-500 disabled:opacity-75 transition-colors ${isEditMode ? 'bg-white' : 'bg-slate-50'}`}
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Email Address</label>
            <input 
              type="email" 
              name="email"
              value={formData.email}
              disabled={true} 
              required
              title="Email address cannot be changed"
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 focus:outline-none focus:border-sky-500 disabled:opacity-75 transition-colors cursor-not-allowed"
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Contact Number</label>
            <input 
              type="text" 
              name="phone"
              value={formData.phone}
              onChange={handleInputChange}
              disabled={!isEditMode} 
              required
              className={`w-full px-4 py-3 border border-slate-200 rounded-xl text-sm text-slate-800 focus:outline-none focus:border-sky-500 disabled:opacity-75 transition-colors ${isEditMode ? 'bg-white' : 'bg-slate-50'}`}
            />
          </div>

          {isEditMode && (
            <div className="md:col-span-2 flex justify-end space-x-3 pt-4 border-t border-slate-100">
              <button 
                type="button" 
                onClick={toggleEditMode} 
                className="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl transition-colors"
              >
                Cancel
              </button>
              <button 
                type="submit" 
                className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl transition-colors shadow-md"
              >
                Save Changes
              </button>
            </div>
          )}

          {/* Change Password Button */}
          <div className="md:col-span-2 mt-6 pt-6 border-t border-slate-200">
            <Link to="/change-password" className="w-full py-2.5 bg-stellarNavy hover:bg-stellarDark text-white text-xs font-bold rounded-xl transition-colors shadow-sm flex items-center justify-center gap-2">
              <Key className="w-4 h-4" /> Change Password
            </Link>
          </div>

          {/* Delete Account Section */}
          <div className="md:col-span-2 mt-6 pt-6 border-t border-slate-200">
            <Link to="/delete-account" className="w-full py-2.5 bg-red-600 hover:bg-red-700 text-white text-xs font-bold rounded-xl transition-colors shadow-sm flex items-center justify-center gap-2">
              <Trash2 className="w-4 h-4" /> Delete Account
            </Link>
            <p className="text-[10px] text-slate-400 text-center mt-2">
              Permanently delete your account and all associated data.
            </p>
          </div>

        </form>
      </div>
    </div>
  );
}
