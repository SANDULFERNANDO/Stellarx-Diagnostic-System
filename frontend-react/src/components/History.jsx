import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { FolderHeart, ArrowLeft, Filter, ChevronRight } from 'lucide-react';
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
      // Create a local map for images to avoid a waterfall of requests blocking rendering
      const fetchedCases = await api.listCases(filters);
      
      // Attempt to fetch images for each case concurrently
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

  return (
    <div className="p-6 md:p-10 space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Case History</h1>
          <p className="text-sm text-slate-500 font-medium">Review all previously analyzed diagnostic records and AI predictions.</p>
        </div>
        <Link 
          to="/dashboard" 
          className="px-4 py-2 bg-white border border-slate-200 hover:border-slate-300 rounded-xl text-xs font-bold text-slate-700 shadow-sm transition-colors flex items-center justify-center gap-1.5 w-fit"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Dashboard
        </Link>
      </div>

      <hr className="border-slate-200/80" />

      {/* Filter Section */}
      <div className="bg-white rounded-xl border border-slate-200/60 shadow-sm p-4 space-y-3">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-stellarNavy" />
          <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">Filter Cases</span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div>
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Case ID</label>
            <input
              type="text"
              value={filterCaseId}
              onChange={(e) => setFilterCaseId(e.target.value)}
              placeholder="Search by Case ID..."
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-stellarNavy transition-colors"
            />
          </div>
          
          <div>
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Status</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-stellarNavy transition-colors bg-white"
            >
              <option value="">All Statuses</option>
              <option value="DRAFT">Draft</option>
              <option value="READY_FOR_ANALYSIS">Ready for Analysis</option>
              <option value="COMPLETED">Completed</option>
              <option value="REVIEWED">Reviewed</option>
            </select>
          </div>
          
          <div>
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">From Date</label>
            <input
              type="date"
              value={filterStartDate}
              onChange={(e) => setFilterStartDate(e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-stellarNavy transition-colors"
            />
          </div>
          
          <div>
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">To Date</label>
            <input
              type="date"
              value={filterEndDate}
              onChange={(e) => setFilterEndDate(e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-stellarNavy transition-colors"
            />
          </div>
        </div>
        
        <div className="flex items-center justify-end gap-3 pt-2">
          <button
            onClick={handleApplyFilters}
            className="px-4 py-2 bg-stellarNavy hover:bg-stellarDark text-white text-xs font-bold rounded-lg transition-colors shadow-sm"
          >
            Apply Filters
          </button>
          <button
            onClick={handleClearFilters}
            className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-lg transition-colors"
          >
            Clear
          </button>
        </div>
      </div>

      {/* History Grid Wrapper */}
      <div className="bg-white rounded-xl border border-slate-200/60 shadow-sm p-6 space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-slate-100">
          <h2 className="text-base font-black text-slate-900 tracking-tight flex items-center gap-2">
            <FolderHeart className="w-4 h-4 text-stellarNavy" /> All Diagnostic Logs
          </h2>
          <span className="text-xs font-bold bg-slate-100 text-slate-600 px-2.5 py-1 rounded-full">
            Total: {cases.length} Cases
          </span>
        </div>

        <div className="space-y-3 pt-2">
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-pulse text-slate-400 text-sm font-medium">Loading...</div>
            </div>
          ) : error ? (
            <p className="text-xs font-medium text-red-500 py-8 text-center">{error}</p>
          ) : cases.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-xs font-medium text-slate-400">No cases found.</p>
              <p className="text-xs text-slate-300 mt-1">Try adjusting your filters or start a new case.</p>
            </div>
          ) : (
            cases.map(item => {
              const prediction = item.diagnosis_result || 'Pending';
              const status = item.status || 'DRAFT';
              const isCompleted = status === 'COMPLETED';
              const isDraft = status === 'DRAFT';
              
              let badgeColor = 'bg-slate-50 text-slate-600 border-slate-200';
              if (isCompleted) badgeColor = 'bg-emerald-50 text-emerald-700 border-emerald-100';
              if (isDraft) badgeColor = 'bg-amber-50 text-amber-700 border-amber-100';
              
              const confidenceText = isCompleted ? 'Completed' : 'In Progress';
              
              return (
                <div 
                  key={item.case_id}
                  onClick={() => {
                    localStorage.setItem('current_case_id', item.case_id);
                    navigate('/result');
                  }}
                  className="bg-white rounded-xl border border-slate-200/60 p-4 shadow-sm flex items-center justify-between group hover:border-slate-300 hover:shadow-md cursor-pointer transition-all"
                >
                  <div className="grid grid-cols-4 gap-4 md:gap-12 flex-1">
                    <div>
                      <span className="block text-[9px] font-bold text-slate-400 uppercase tracking-wider">Case ID</span>
                      <span className="text-xs font-black text-slate-800 truncate block">{item.case_id || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="block text-[9px] font-bold text-slate-400 uppercase tracking-wider">Date</span>
                      <span className="text-xs font-semibold text-slate-500">{item.case_date || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="block text-[9px] font-bold text-slate-400 uppercase tracking-wider">Top Prediction</span>
                      <span className="text-xs font-black text-slate-800 block truncate">{prediction}</span>
                    </div>
                    <div>
                      <span className="block text-[9px] font-bold text-slate-400 uppercase tracking-wider">Images</span>
                      <span className="text-xs font-black text-slate-800">{item.imageCount}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3 pl-4">
                    <span className={`px-3 py-1 text-[10px] font-bold rounded-full ${badgeColor}`}>
                      {confidenceText}
                    </span>
                    <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-slate-600 group-hover:translate-x-0.5 transition-all" />
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
