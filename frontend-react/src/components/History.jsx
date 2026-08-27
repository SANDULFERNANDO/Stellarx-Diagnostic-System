import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { FolderHeart, ArrowLeft, Filter, ChevronRight, Search, Calendar, FileText, Activity, ImageIcon } from 'lucide-react';
import { motion } from 'framer-motion';
import { api } from '../services/api';

export default function History() {
  const [cases, setCases] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Filters
  const [filterCaseId, setFilterCaseId] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterStartDate, setFilterStartDate] = useState('');
  const [filterEndDate, setFilterEndDate] = useState('');

  const navigate = useNavigate();

  const loadCases = async (filters = {}) => {
    setIsLoading(true);
    setError('');
    try {
      const fetchedCases = await api.listCases(filters);
      
      const casesWithImages = await Promise.all(
        (fetchedCases || []).map(async (item) => {
          let imageCount = 0;
          try {
            const imagesRes = await api.getCaseImages(item.case_id);
            imageCount = imagesRes.total || imagesRes.images?.length || 0;
          } catch {
            // Ignore individual image fetch errors
          }
          return { ...item, imageCount };
        })
      );
      
      setCases(casesWithImages);
    } catch (err) {
      setError(err.message || 'Failed to load cases');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!api.isAuthenticated()) {
      navigate('/login');
      return;
    }
    loadCases();
  }, [navigate]);

  const handleApplyFilters = () => {
    const filters = {};
    if (filterCaseId.trim()) filters.case_id = filterCaseId.trim();
    if (filterStatus) filters.status = filterStatus;
    if (filterStartDate) filters.start_date = filterStartDate;
    if (filterEndDate) filters.end_date = filterEndDate;
    loadCases(filters);
  };

  const handleClearFilters = () => {
    setFilterCaseId('');
    setFilterStatus('');
    setFilterStartDate('');
    setFilterEndDate('');
    loadCases();
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
    hidden: { opacity: 0, y: 15 },
    show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 24 } }
  };

  return (
    <motion.div 
      initial="hidden"
      animate="show"
      variants={containerVariants}
      className="p-6 md:p-10 space-y-6 max-w-6xl mx-auto"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex flex-col md:flex-row md:items-end justify-between gap-6 bg-white p-8 rounded-3xl shadow-sm border border-slate-100 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-brand-secondary/5 to-brand-primary/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3 pointer-events-none" />
        
        <div className="space-y-3 relative z-10">
          <div className="flex items-center space-x-2 text-brand-secondary">
            <FolderHeart className="w-5 h-5" />
            <span className="text-xs font-bold uppercase tracking-wider">Patient Records</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-black text-slate-800 tracking-tight">Case History</h1>
          <p className="text-sm md:text-base text-slate-500 font-medium max-w-xl leading-relaxed">
            Review all previously analyzed diagnostic records, track patient progress, and review AI predictions.
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

      {/* Filter Section */}
      <motion.div variants={itemVariants} className="bg-white rounded-3xl border border-slate-100 shadow-sm p-6 space-y-5">
        <div className="flex items-center gap-2 border-b border-slate-100 pb-4">
          <Filter className="w-5 h-5 text-brand-primary" />
          <h2 className="text-sm font-black text-slate-800 uppercase tracking-wider">Filter Cases</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Case ID</label>
            <div className="relative group">
              <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400 group-focus-within:text-brand-primary transition-colors" />
              <input
                type="text"
                value={filterCaseId}
                onChange={(e) => setFilterCaseId(e.target.value)}
                placeholder="Search ID..."
                className="w-full pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-200 focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 rounded-xl text-sm font-medium text-slate-800 outline-none transition-all"
              />
            </div>
          </div>
          
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Status</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 rounded-xl text-sm font-medium text-slate-800 outline-none transition-all cursor-pointer"
            >
              <option value="">All Statuses</option>
              <option value="DRAFT">Draft</option>
              <option value="READY_FOR_ANALYSIS">Ready for Analysis</option>
              <option value="COMPLETED">Completed</option>
              <option value="REVIEWED">Reviewed</option>
            </select>
          </div>
          
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">From Date</label>
            <div className="relative group">
              <Calendar className="w-4 h-4 absolute left-3 top-3 text-slate-400 group-focus-within:text-brand-primary transition-colors" />
              <input
                type="date"
                value={filterStartDate}
                onChange={(e) => setFilterStartDate(e.target.value)}
                className="w-full pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-200 focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 rounded-xl text-sm font-medium text-slate-800 outline-none transition-all"
              />
            </div>
          </div>
          
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">To Date</label>
            <div className="relative group">
              <Calendar className="w-4 h-4 absolute left-3 top-3 text-slate-400 group-focus-within:text-brand-primary transition-colors" />
              <input
                type="date"
                value={filterEndDate}
                onChange={(e) => setFilterEndDate(e.target.value)}
                className="w-full pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-200 focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 rounded-xl text-sm font-medium text-slate-800 outline-none transition-all"
              />
            </div>
          </div>
        </div>
        
        <div className="flex items-center justify-end gap-3 pt-2">
          <button
            onClick={handleClearFilters}
            className="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-bold rounded-xl transition-colors"
          >
            Clear Filters
          </button>
          <button
            onClick={handleApplyFilters}
            className="px-5 py-2.5 bg-brand-primary hover:bg-stellarDark text-white text-sm font-bold rounded-xl transition-all shadow-md hover:shadow-lg active:scale-[0.98]"
          >
            Apply Filters
          </button>
        </div>
      </motion.div>

      {/* History List */}
      <motion.div variants={itemVariants} className="bg-white rounded-3xl border border-slate-100 shadow-sm p-6 space-y-4">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <h2 className="text-lg font-black text-slate-800 tracking-tight flex items-center gap-2">
            <FileText className="w-5 h-5 text-brand-secondary" /> Diagnostic Logs
          </h2>
          <span className="text-xs font-bold bg-slate-100 text-slate-600 px-3 py-1.5 rounded-full flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-brand-primary" />
            {cases.length} Cases Total
          </span>
        </div>

        <div className="space-y-3 pt-2">
          {isLoading ? (
            <div className="text-center py-16">
              <div className="w-10 h-10 border-4 border-brand-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-sm font-medium text-slate-500">Loading cases...</p>
            </div>
          ) : error ? (
            <div className="bg-red-50 rounded-2xl border border-red-100 p-8 text-center shadow-sm">
              <p className="text-sm font-bold text-red-600 mb-1">Failed to load cases</p>
              <p className="text-xs font-medium text-red-500">{error}</p>
            </div>
          ) : cases.length === 0 ? (
            <div className="bg-slate-50 rounded-2xl border border-slate-200 border-dashed p-16 text-center">
              <FolderHeart className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <p className="text-base font-bold text-slate-600 mb-1">No cases found</p>
              <p className="text-sm font-medium text-slate-500">Try adjusting your filters or start a new case from the dashboard.</p>
            </div>
          ) : (
            cases.map((item, index) => {
              const prediction = item.diagnosis_result || 'Pending';
              const status = item.status || 'DRAFT';
              const isCompleted = status === 'COMPLETED';
              const isDraft = status === 'DRAFT';
              
              let badgeColor = 'bg-slate-50 text-slate-600 border-slate-200';
              if (isCompleted) badgeColor = 'bg-emerald-50 text-emerald-700 border-emerald-200';
              if (isDraft) badgeColor = 'bg-amber-50 text-amber-700 border-amber-200';
              
              const confidenceText = isCompleted ? 'Completed' : 'Processing';
              
              return (
                <motion.div 
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  key={item.case_id}
                  onClick={() => {
                    localStorage.setItem('current_case_id', item.case_id);
                    navigate('/result');
                  }}
                  className="bg-white rounded-2xl border border-slate-100 p-5 hover:bg-slate-50 flex flex-col md:flex-row md:items-center justify-between group cursor-pointer transition-all hover:shadow-md hover:border-slate-200 gap-4"
                >
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-6 flex-1 items-center">
                    <div>
                      <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Case ID</span>
                      <span className="text-sm font-black text-slate-700 truncate font-mono bg-slate-100 px-2 py-0.5 rounded text-xs">{item.case_id?.substring(0, 8) || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Date</span>
                      <span className="text-sm font-semibold text-slate-600 flex items-center gap-1.5">
                        <Calendar className="w-3.5 h-3.5 text-slate-400" />
                        {item.case_date || 'N/A'}
                      </span>
                    </div>
                    <div>
                      <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Images</span>
                      <span className="text-sm font-bold text-slate-700 flex items-center gap-1.5">
                        <ImageIcon className="w-3.5 h-3.5 text-slate-400" />
                        {item.imageCount} attached
                      </span>
                    </div>
                    <div>
                      <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Top Prediction</span>
                      <span className="text-sm font-black text-brand-primary block truncate flex items-center gap-1.5">
                        <Activity className="w-3.5 h-3.5 text-brand-secondary" />
                        {prediction}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between md:justify-end w-full md:w-auto space-x-4 pl-0 md:pl-4 mt-2 md:mt-0">
                    <span className={`px-3 py-1.5 text-xs font-bold rounded-lg border ${badgeColor}`}>
                      {confidenceText}
                    </span>
                    <div className="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center group-hover:bg-brand-primary group-hover:text-white transition-all text-slate-400 border border-slate-200 group-hover:border-brand-primary">
                      <ChevronRight className="w-4 h-4" />
                    </div>
                  </div>
                </motion.div>
              );
            })
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
