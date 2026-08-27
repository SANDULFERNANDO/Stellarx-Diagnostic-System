import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { Layers, LayoutDashboard, User, LogOut } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState } from 'react';
import { api } from '../services/api';

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const [userInitials, setUserInitials] = useState('MD');
  const [userName, setUserName] = useState('Doctor');

  useEffect(() => {
    const user = api.getUser();
    if (user) {
      const name = user.first_name || user.name || user.username || 'Doctor';
      setUserName(name);
      setUserInitials(name.substring(0, 2).toUpperCase());
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Profile', path: '/profile', icon: User },
  ];

  return (
    <div className="bg-bgGray min-h-screen flex flex-col md:flex-row overflow-hidden font-sans text-slate-800">
      {/* Sidebar */}
      <aside className="w-full md:w-64 bg-stellarNavy text-white flex flex-col justify-between p-6 shrink-0 relative z-20 shadow-2xl md:shadow-[4px_0_24px_rgba(15,74,115,0.15)] md:h-screen md:sticky top-0">
        
        {/* Abstract background glow for the sidebar */}
        <div className="absolute top-0 left-0 w-full h-64 bg-gradient-to-b from-brand-secondary/20 to-transparent opacity-50 pointer-events-none rounded-tr-3xl" />

        <div className="space-y-10 relative z-10">
          <div className="flex items-center space-x-3 cursor-pointer group" onClick={() => navigate('/dashboard')}>
            <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center group-hover:bg-white/20 transition-colors shadow-inner backdrop-blur-sm border border-white/5">
              <Layers className="w-5 h-5 text-sky-300" />
            </div>
            <span className="text-2xl font-black tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-sky-100">StellarX</span>
          </div>
          
          <nav className="space-y-3 relative">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname.startsWith(item.path);
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  className="relative flex items-center space-x-4 px-4 py-3.5 rounded-xl text-sm font-bold transition-colors group overflow-hidden"
                >
                  {/* Active background pill via Framer Motion */}
                  {isActive && (
                    <motion.div 
                      layoutId="sidebar-active-pill"
                      className="absolute inset-0 bg-white/10 rounded-xl border border-white/10 shadow-[inset_0_1px_2px_rgba(255,255,255,0.1)]"
                      initial={false}
                      transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                    />
                  )}
                  
                  {/* Hover background for non-active items */}
                  {!isActive && (
                    <div className="absolute inset-0 bg-white/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity" />
                  )}

                  <Icon className={`w-4 h-4 relative z-10 transition-colors ${isActive ? 'text-sky-300' : 'text-slate-400 group-hover:text-sky-200'}`} />
                  <span className={`relative z-10 transition-colors ${isActive ? 'text-white' : 'text-slate-300 group-hover:text-white'}`}>
                    {item.name}
                  </span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="relative z-10 space-y-4">
          {/* User Snapshot Mini-Profile */}
          <div className="flex items-center space-x-3 px-3 py-3 bg-stellarDark/50 rounded-2xl border border-white/5 backdrop-blur-sm">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-sky-400 to-blue-600 flex items-center justify-center text-xs font-black shadow-md border border-white/10">
              {userInitials}
            </div>
            <div className="flex-1 overflow-hidden">
              <p className="text-xs font-bold text-white truncate">{userName}</p>
              <p className="text-[10px] font-semibold text-sky-200/70 uppercase tracking-wider truncate">Clinician</p>
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="flex items-center space-x-3 px-4 py-3 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl text-sm font-bold transition-all w-full text-left group"
          >
            <LogOut className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            <span>Log Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto h-screen relative z-10">
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="min-h-full"
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}
