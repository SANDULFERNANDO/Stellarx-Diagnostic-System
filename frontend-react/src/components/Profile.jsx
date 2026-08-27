import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { User, Edit3, Key, Trash2, ArrowLeft, ShieldCheck, Mail, Phone, Briefcase, ChevronRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
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
    
    // Custom toast notification could be added here
  };

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 24 } }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-12 h-12 border-4 border-brand-primary border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const displayName = formData.name;
  const displayPosition = formData.position;

  return (
    <motion.div 
      initial="hidden"
      animate="show"
      variants={containerVariants}
      className="p-6 md:p-10 max-w-5xl mx-auto w-full space-y-8 pb-24"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex flex-col md:flex-row md:items-end justify-between gap-6 bg-white p-8 rounded-3xl shadow-sm border border-slate-100 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-brand-secondary/5 to-brand-primary/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3 pointer-events-none" />
        
        <div className="space-y-3 relative z-10">
          <div className="flex items-center space-x-2 text-brand-secondary">
            <ShieldCheck className="w-5 h-5" />
            <span className="text-xs font-bold uppercase tracking-wider">Account Settings</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-black text-slate-800 tracking-tight">User Profile</h1>
          <p className="text-sm md:text-base text-slate-500 font-medium max-w-xl leading-relaxed">
            Manage your practitioner credentials, contact information, and security settings.
          </p>
        </div>
        
        <div className="relative z-10 shrink-0 flex gap-3">
          <Link 
            to="/dashboard" 
            className="px-5 py-2.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 hover:border-slate-300 rounded-xl text-sm font-bold text-slate-700 shadow-sm transition-all flex items-center justify-center gap-2 group"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" /> Back
          </Link>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column (Profile & Form) */}
        <div className="lg:col-span-8 space-y-8">
          <motion.div variants={itemVariants} className="bg-white rounded-3xl border border-slate-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-8 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-32 bg-gradient-to-r from-brand-primary/10 to-brand-secondary/10" />
            
            {/* Top Profile Overview Layer */}
            <div className="flex flex-col sm:flex-row items-center sm:items-end space-y-4 sm:space-y-0 sm:space-x-6 relative z-10 pt-12 pb-8 border-b border-slate-100">
              <div className="w-28 h-28 bg-white rounded-2xl flex items-center justify-center text-brand-primary border-4 border-white shadow-lg shrink-0 relative group">
                <User className="w-12 h-12" />
                <div className="absolute inset-0 bg-black/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center cursor-pointer">
                  <Edit3 className="w-5 h-5 text-slate-700" />
                </div>
              </div>
              <div className="text-center sm:text-left flex-1 pb-2">
                <h2 className="text-2xl font-black text-slate-800 tracking-tight">{displayName}</h2>
                <p className="text-sm font-bold text-brand-secondary mt-1">{displayPosition}</p>
                <div className="flex items-center justify-center sm:justify-start gap-2 mt-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                  <span className="text-xs text-slate-500 font-medium uppercase tracking-wider">Active Account</span>
                </div>
              </div>
              <div className="pb-2">
                <button 
                  onClick={toggleEditMode} 
                  className={`px-5 py-2.5 text-sm font-bold rounded-xl transition-all shadow-sm flex items-center space-x-2 border ${isEditMode ? 'bg-white border-slate-300 text-slate-700 hover:bg-slate-50' : 'bg-brand-primary hover:bg-stellarDark text-white border-transparent shadow-brand-primary/20 hover:-translate-y-0.5'}`}
                >
                  <Edit3 className="w-4 h-4" />
                  <span>{isEditMode ? 'Cancel Edit' : 'Edit Profile'}</span>
                </button>
              </div>
            </div>

            {/* Detail Input Fields Grid Form */}
            <form onSubmit={handleSave} className="pt-8">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                    <User className="w-3.5 h-3.5" /> Full Name
                  </label>
                  <input 
                    type="text" 
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    disabled={!isEditMode} 
                    required
                    className={`w-full px-4 py-3 border rounded-xl text-sm font-medium focus:outline-none transition-colors ${isEditMode ? 'bg-white border-slate-200 focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 text-slate-800' : 'bg-slate-50 border-slate-100 text-slate-600'}`}
                  />
                </div>
                
                <div className="space-y-2">
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                    <Briefcase className="w-3.5 h-3.5" /> Position / Title
                  </label>
                  <input 
                    type="text" 
                    name="position"
                    value={formData.position}
                    onChange={handleInputChange}
                    disabled={!isEditMode} 
                    required 
                    placeholder="e.g. Dermatologist"
                    className={`w-full px-4 py-3 border rounded-xl text-sm font-medium focus:outline-none transition-colors ${isEditMode ? 'bg-white border-slate-200 focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 text-slate-800' : 'bg-slate-50 border-slate-100 text-slate-600'}`}
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                    <Mail className="w-3.5 h-3.5" /> Email Address
                  </label>
                  <div className="relative">
                    <input 
                      type="email" 
                      name="email"
                      value={formData.email}
                      disabled={true} 
                      required
                      title="Email address cannot be changed"
                      className="w-full pl-4 pr-10 py-3 bg-slate-100 border border-slate-200 rounded-xl text-sm font-medium text-slate-500 focus:outline-none cursor-not-allowed"
                    />
                    <div className="absolute right-3 top-3.5 w-4 h-4 rounded-full border-2 border-slate-300 flex items-center justify-center group" title="Email cannot be changed">
                      <div className="w-2 h-0.5 bg-slate-300 rounded"></div>
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                    <Phone className="w-3.5 h-3.5" /> Contact Number
                  </label>
                  <input 
                    type="text" 
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    disabled={!isEditMode} 
                    required
                    className={`w-full px-4 py-3 border rounded-xl text-sm font-medium focus:outline-none transition-colors ${isEditMode ? 'bg-white border-slate-200 focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 text-slate-800' : 'bg-slate-50 border-slate-100 text-slate-600'}`}
                  />
                </div>
              </div>

              <AnimatePresence>
                {isEditMode && (
                  <motion.div 
                    initial={{ opacity: 0, height: 0, marginTop: 0 }}
                    animate={{ opacity: 1, height: 'auto', marginTop: 32 }}
                    exit={{ opacity: 0, height: 0, marginTop: 0 }}
                    className="flex justify-end space-x-3 overflow-hidden"
                  >
                    <button 
                      type="button" 
                      onClick={toggleEditMode} 
                      className="px-6 py-3 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 text-sm font-bold rounded-xl transition-colors"
                    >
                      Discard
                    </button>
                    <button 
                      type="submit" 
                      className="px-8 py-3 bg-brand-primary hover:bg-stellarDark text-white text-sm font-bold rounded-xl transition-all shadow-md hover:shadow-lg hover:-translate-y-0.5"
                    >
                      Save Changes
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </form>
          </motion.div>
        </div>

        {/* Right Column (Security & Danger Zone) */}
        <div className="lg:col-span-4 space-y-6">
          <motion.div variants={itemVariants} className="bg-white rounded-3xl border border-slate-100 shadow-sm p-6 space-y-6">
            <h3 className="text-sm font-black text-slate-800 flex items-center gap-2 pb-3 border-b border-slate-100">
              <ShieldCheck className="w-5 h-5 text-brand-secondary" /> Security
            </h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-slate-800">Password</h4>
                  <p className="text-[11px] font-medium text-slate-500 mt-0.5">Last changed 3 months ago</p>
                </div>
              </div>
              
              <Link to="/change-password" className="w-full py-3 bg-white border border-slate-200 hover:border-brand-primary hover:text-brand-primary text-slate-700 text-sm font-bold rounded-xl transition-all flex items-center justify-between group px-4">
                <span className="flex items-center gap-2"><Key className="w-4 h-4" /> Change Password</span>
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-brand-primary group-hover:translate-x-1 transition-all" />
              </Link>
            </div>
          </motion.div>

          <motion.div variants={itemVariants} className="bg-white rounded-3xl border border-red-100 shadow-sm p-6 space-y-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-red-50 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2" />
            
            <div className="relative z-10">
              <h3 className="text-sm font-black text-red-600 flex items-center gap-2 pb-3 border-b border-red-100/50">
                <Trash2 className="w-5 h-5" /> Danger Zone
              </h3>
              
              <div className="pt-4 space-y-4">
                <p className="text-[11px] font-medium text-slate-600 leading-relaxed">
                  Permanently delete your account and all associated data, including patient records and history logs. This action cannot be undone.
                </p>
                
                <Link to="/delete-account" className="w-full py-3 bg-red-50 hover:bg-red-600 text-red-600 hover:text-white border border-red-100 hover:border-red-600 text-sm font-bold rounded-xl transition-all flex items-center justify-center gap-2 group">
                  <Trash2 className="w-4 h-4" /> Delete Account
                </Link>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}
