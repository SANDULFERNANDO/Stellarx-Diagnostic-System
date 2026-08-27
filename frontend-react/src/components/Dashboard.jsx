import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Plus, Clock, ChevronRight } from 'lucide-react';
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

  const userName = user?.first_name || user?.name || user?.username || 'User';
  const totalCases = cases.length;
  const recentAnalyses = Math.min(cases.length, 15);
  const lastAnalysisDate = cases.length > 0 && cases[0].created_at 
    ? new Date(cases[0].created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) 
    : 'N/A';

  return (
    <div className="p-6 md:p-10 space-y-8 max-w-5xl mx-auto">
      {/* Welcome Heading */}
      <div className="space-y-1">
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">
          Welcome, <span className="text-slate-900">{userName}</span>
        </h1>
        <p className="text-sm text-slate-500 font-medium">
          Use the system to submit clinical images and symptoms for AI-assisted skin condition analysis.
        </p>
      </div>

      <hr className="border-slate-200/80" />

      {/* System Overview */}
      <div className="space-y-4">
        <h2 className="text-lg font-black text-slate-900 tracking-tight">System Overview</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-white rounded-xl border border-slate-200/60 p-5 shadow-sm space-y-2">
            <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Cases</span>
            <span className="block text-3xl font-black text-stellarNavy">{totalCases}</span>
          </div>
          <div className="bg-white rounded-xl border border-slate-200/60 p-5 shadow-sm space-y-2">
            <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Recent Analyses</span>
            <span className="block text-3xl font-black text-slate-800">{recentAnalyses}</span>
          </div>
          <div className="bg-white rounded-xl border border-slate-200/60 p-5 shadow-sm space-y-2">
            <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Last Analysis</span>
            <span className="block text-sm font-black text-slate-800 pt-2">{lastAnalysisDate}</span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="space-y-4">
        <h2 className="text-lg font-black text-slate-900 tracking-tight">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Create New Case */}
          <div className="bg-white rounded-xl border border-slate-200/60 p-6 flex flex-col justify-between shadow-sm space-y-4">
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-sky-50 text-stellarNavy rounded-full flex items-center justify-center shrink-0">
                <Plus className="w-6 h-6" />
              </div>
              <div className="space-y-1">
                <h3 className="text-sm font-black text-slate-800">Create New Case</h3>
                <p className="text-xs text-slate-400 font-medium leading-relaxed">
                  Start a new diagnostic case by entering patient information, uploading an image, and recording symptoms.
                </p>
              </div>
            </div>
            <button 
              onClick={() => navigate('/symptoms')} 
              className="w-full py-2.5 bg-stellarNavy hover:bg-stellarDark text-white text-xs font-bold rounded-lg transition-colors shadow-sm"
            >
              Start New Case
            </button>
          </div>

          {/* View Case History */}
          <div className="bg-white rounded-xl border border-slate-200/60 p-6 flex flex-col justify-between shadow-sm space-y-4">
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-slate-50 text-slate-600 rounded-full flex items-center justify-center shrink-0">
                <Clock className="w-5 h-5" />
              </div>
              <div className="space-y-1">
                <h3 className="text-sm font-black text-slate-800">View Case History</h3>
                <p className="text-xs text-slate-400 font-medium leading-relaxed">
                  Review previously analyzed cases and view detailed diagnostic results.
                </p>
              </div>
            </div>
            <button 
              onClick={() => navigate('/history')} 
              className="w-full py-2.5 border border-stellarNavy text-stellarNavy bg-white hover:bg-slate-50 text-xs font-bold rounded-lg transition-colors"
            >
              Open Case History
            </button>
          </div>
        </div>
      </div>

      {/* Recent Case Activity */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-black text-slate-900 tracking-tight">Recent Case Activity</h2>
          <Link to="/history" className="text-xs font-bold text-stellarNavy hover:underline flex items-center space-x-1">
            <span>View All</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="space-y-3">
          {isLoading ? (
            <p className="text-xs font-medium text-slate-400 py-8 text-center">Loading cases...</p>
          ) : error ? (
            <div className="bg-white rounded-xl border border-slate-200/60 p-6 text-center">
              <p className="text-xs font-medium text-red-500">Failed to load cases: {error}</p>
            </div>
          ) : cases.length === 0 ? (
            <div className="bg-white rounded-xl border border-slate-200/60 p-6 text-center">
              <p className="text-xs font-medium text-slate-400">No cases yet. Start your first case!</p>
            </div>
          ) : (
            cases.slice(0, 5).map(item => {
              const prediction = item.diagnosis_result || 'Pending';
              const status = item.status || 'DRAFT';
              const isCompleted = status === 'COMPLETED';
              const badgeColor = isCompleted ? 'bg-emerald-50 text-emerald-700 border-emerald-100' : 'bg-amber-50 text-amber-700 border-amber-100';
              const confidenceText = isCompleted ? 'Completed' : 'In Progress';
              
              return (
                <div 
                  key={item.case_id || Math.random()} 
                  onClick={() => {
                    localStorage.setItem('current_case_id', item.case_id);
                    navigate('/result');
                  }}
                  className="bg-white rounded-xl border border-slate-200/60 p-4 shadow-sm flex items-center justify-between group hover:border-slate-300 transition-colors cursor-pointer"
                >
                  <div className="grid grid-cols-3 gap-4 md:gap-12 flex-1">
                    <div>
                      <span className="block text-[9px] font-bold text-slate-400 uppercase tracking-wider">Case ID</span>
                      <span className="text-xs font-black text-slate-800 truncate">{item.case_id || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="block text-[9px] font-bold text-slate-400 uppercase tracking-wider">Date</span>
                      <span className="text-xs font-semibold text-slate-500">{item.case_date || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="block text-[9px] font-bold text-slate-400 uppercase tracking-wider">Top Prediction</span>
                      <span className="text-xs font-black text-slate-800 block truncate">{prediction}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3 pl-4">
                    <span className={`px-3 py-1 text-[10px] font-bold rounded-full ${badgeColor}`}>
                      {confidenceText}
                    </span>
                    <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-slate-600 transition-colors" />
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
