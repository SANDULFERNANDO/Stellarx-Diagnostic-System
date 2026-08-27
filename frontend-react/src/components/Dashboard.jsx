import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Plus, Clock, ChevronRight, Activity, FileText, LayoutDashboard, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';
import { api } from '../services/api';

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [cases, setCases] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
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
          console.warn('Could not fetch user', err);
        }
      }
      setUser(currentUser);
    };

    const loadCases = async () => {
      try {
        const fetchedCases = await api.listCases();
        setCases(fetchedCases || []);
      } catch (err) {
        setError(err.message || 'Failed to load cases');
      } finally {
        setIsLoading(false);
      }
    };

    loadUser();
    loadCases();
  }, [navigate]);

  const userName = user?.first_name || user?.name || user?.username || 'Doctor';
  const totalCases = cases.length;
  const recentAnalyses = Math.min(cases.length, 15);
  const lastAnalysisDate = cases.length > 0 && cases[0].created_at 
    ? new Date(cases[0].created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) 
    : 'N/A';

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 15 },
    show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 24 } }
  };

  return (
    <motion.div 
      initial="hidden"
      animate="show"
      variants={containerVariants}
      className="p-6 md:p-10 space-y-8 max-w-6xl mx-auto"
    >
      {/* Welcome Heading */}
      <motion.div variants={itemVariants} className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-8 rounded-3xl shadow-sm border border-slate-100 relative overflow-hidden">
        {/* Subtle Background Elements */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-brand-primary/5 to-brand-secondary/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3 pointer-events-none" />
        
        <div className="space-y-2 relative z-10">
          <div className="flex items-center space-x-2 text-brand-secondary mb-1">
            <Sparkles className="w-4 h-4" />
            <span className="text-xs font-bold uppercase tracking-wider">AI Diagnostic Network</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-black text-slate-800 tracking-tight">
            Welcome back, <span className="text-brand-primary">{userName}</span>
          </h1>
          <p className="text-sm md:text-base text-slate-500 font-medium max-w-xl leading-relaxed">
            Submit clinical images and symptoms for state-of-the-art AI-assisted skin condition analysis and diagnostics.
          </p>
        </div>
        
        <div className="relative z-10 shrink-0 hidden md:block">
          <div className="w-16 h-16 bg-brand-primary/10 rounded-2xl flex items-center justify-center rotate-3 shadow-inner">
            <LayoutDashboard className="w-8 h-8 text-brand-primary -rotate-3" />
          </div>
        </div>
      </motion.div>

      {/* System Overview */}
      <motion.div variants={itemVariants} className="space-y-4">
        <h2 className="text-lg font-black text-slate-800 tracking-tight flex items-center space-x-2">
          <Activity className="w-5 h-5 text-brand-secondary" />
          <span>System Overview</span>
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 md:gap-6">
          <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-sm hover:shadow-md transition-shadow group relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <FileText className="w-16 h-16 text-brand-primary" />
            </div>
            <span className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 relative z-10">Total Cases</span>
            <span className="block text-4xl font-black text-brand-primary relative z-10">{totalCases}</span>
          </div>
          <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-sm hover:shadow-md transition-shadow group relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Activity className="w-16 h-16 text-emerald-600" />
            </div>
            <span className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 relative z-10">Recent Analyses</span>
            <span className="block text-4xl font-black text-slate-800 relative z-10">{recentAnalyses}</span>
          </div>
          <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-sm hover:shadow-md transition-shadow group relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Clock className="w-16 h-16 text-brand-secondary" />
            </div>
            <span className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 relative z-10">Last Analysis</span>
            <span className="block text-lg font-bold text-slate-800 pt-1 relative z-10">{lastAnalysisDate}</span>
          </div>
        </div>
      </motion.div>

      {/* Quick Actions */}
      <motion.div variants={itemVariants} className="space-y-4">
        <h2 className="text-lg font-black text-slate-800 tracking-tight flex items-center space-x-2">
          <Sparkles className="w-5 h-5 text-amber-500" />
          <span>Quick Actions</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
          {/* Create New Case */}
          <div className="bg-gradient-to-br from-brand-primary to-brand-secondary rounded-2xl p-6 md:p-8 flex flex-col justify-between shadow-lg text-white group relative overflow-hidden">
            <div className="absolute top-[-20%] right-[-10%] w-[50%] h-[150%] bg-white/10 rotate-12 blur-2xl pointer-events-none" />
            <div className="flex items-start space-x-4 relative z-10 mb-8">
              <div className="w-14 h-14 bg-white/20 backdrop-blur-md rounded-2xl flex items-center justify-center shrink-0 border border-white/20">
                <Plus className="w-7 h-7 text-white" />
              </div>
              <div className="space-y-2 mt-1">
                <h3 className="text-lg font-black tracking-tight">Create New Case</h3>
                <p className="text-sm text-sky-100 font-medium leading-relaxed">
                  Start a new diagnostic case by entering patient information, uploading an image, and recording symptoms.
                </p>
              </div>
            </div>
            <button 
              onClick={() => navigate('/symptoms')} 
              className="w-full py-3.5 bg-white text-brand-primary hover:bg-sky-50 text-sm font-bold rounded-xl transition-all shadow-md hover:shadow-lg active:scale-[0.99] relative z-10 flex items-center justify-center space-x-2 group-hover:translate-y-0.5"
            >
              <Plus className="w-4 h-4" />
              <span>Start Diagnostic Case</span>
            </button>
          </div>

          {/* View Case History */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 md:p-8 flex flex-col justify-between shadow-sm group">
            <div className="flex items-start space-x-4 mb-8">
              <div className="w-14 h-14 bg-slate-50 text-slate-600 rounded-2xl flex items-center justify-center shrink-0 border border-slate-100 group-hover:bg-slate-100 transition-colors">
                <Clock className="w-7 h-7" />
              </div>
              <div className="space-y-2 mt-1">
                <h3 className="text-lg font-black text-slate-800 tracking-tight">View Case History</h3>
                <p className="text-sm text-slate-500 font-medium leading-relaxed">
                  Review previously analyzed cases, access detailed diagnostic reports, and track patient progress over time.
                </p>
              </div>
            </div>
            <button 
              onClick={() => navigate('/history')} 
              className="w-full py-3.5 border-2 border-slate-200 text-slate-700 bg-white hover:border-brand-primary hover:text-brand-primary text-sm font-bold rounded-xl transition-all active:scale-[0.99] flex items-center justify-center space-x-2"
            >
              <Clock className="w-4 h-4" />
              <span>Open Case History</span>
            </button>
          </div>
        </div>
      </motion.div>

      {/* Recent Case Activity */}
      <motion.div variants={itemVariants} className="space-y-4 pb-10">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-black text-slate-800 tracking-tight flex items-center space-x-2">
            <FileText className="w-5 h-5 text-slate-400" />
            <span>Recent Activity</span>
          </h2>
          <Link to="/history" className="text-sm font-bold text-brand-primary hover:text-brand-secondary flex items-center space-x-1 group">
            <span>View All</span>
            <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>

        <div className="space-y-3">
          {isLoading ? (
            <div className="bg-white rounded-2xl border border-slate-100 p-12 text-center shadow-sm">
              <div className="w-8 h-8 border-4 border-brand-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-sm font-medium text-slate-500">Loading your recent cases...</p>
            </div>
          ) : error ? (
            <div className="bg-red-50 rounded-2xl border border-red-100 p-8 text-center shadow-sm">
              <p className="text-sm font-bold text-red-600 mb-1">Failed to load cases</p>
              <p className="text-xs font-medium text-red-500">{error}</p>
            </div>
          ) : cases.length === 0 ? (
            <div className="bg-slate-50 rounded-2xl border border-slate-200 border-dashed p-12 text-center">
              <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
              <p className="text-sm font-bold text-slate-600 mb-1">No cases found</p>
              <p className="text-xs font-medium text-slate-500">Your recent diagnostic cases will appear here.</p>
            </div>
          ) : (
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
              {cases.slice(0, 5).map((item, index) => {
                const prediction = item.diagnosis_result || 'Pending';
                const status = item.status || 'DRAFT';
                const isCompleted = status === 'COMPLETED';
                const badgeColor = isCompleted ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-amber-50 text-amber-700 border-amber-200';
                const confidenceText = isCompleted ? 'Completed' : 'Processing';
                
                return (
                  <motion.div 
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    key={item.case_id || Math.random()} 
                    onClick={() => {
                      localStorage.setItem('current_case_id', item.case_id);
                      navigate('/result');
                    }}
                    className="p-5 flex flex-col sm:flex-row sm:items-center justify-between group hover:bg-slate-50 transition-colors cursor-pointer border-b border-slate-100 last:border-b-0 gap-4"
                  >
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-6 flex-1 items-center">
                      <div>
                        <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Case ID</span>
                        <span className="text-sm font-black text-slate-700 truncate font-mono bg-slate-100 px-2 py-0.5 rounded text-xs">{item.case_id?.substring(0, 8) || 'N/A'}</span>
                      </div>
                      <div>
                        <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Date</span>
                        <span className="text-sm font-semibold text-slate-600">{item.case_date || 'N/A'}</span>
                      </div>
                      <div className="col-span-2 md:col-span-1">
                        <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Top Prediction</span>
                        <span className="text-sm font-black text-brand-primary block truncate">{prediction}</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between sm:justify-end w-full sm:w-auto space-x-4 pl-0 sm:pl-4 mt-2 sm:mt-0">
                      <span className={`px-3 py-1.5 text-xs font-bold rounded-lg border ${badgeColor}`}>
                        {confidenceText}
                      </span>
                      <div className="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center group-hover:bg-brand-primary group-hover:text-white transition-all text-slate-400 border border-slate-200 group-hover:border-brand-primary">
                        <ChevronRight className="w-4 h-4" />
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
