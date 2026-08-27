import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Layers, Home, Sparkles, AlertCircle, RefreshCw, Save, Activity, FolderHeart, ShieldCheck, Image } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../services/api';

export default function Result() {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [images, setImages] = useState([]);
  const [symptoms, setSymptoms] = useState([]);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const caseId = localStorage.getItem('current_case_id');
    if (!caseId) {
      alert('No case found. Please start a new case.');
      navigate('/symptoms');
      return;
    }

    const loadData = async () => {
      try {
        // Load analysis result
        const savedResult = localStorage.getItem('current_analysis_result');
        if (savedResult) {
          try {
            const parsed = JSON.parse(savedResult);
            setAnalysisResult(parsed);
          } catch {
            setError('Invalid analysis result.');
          }
        } else {
          setError('Analysis result was not found. Please return to the symptoms page and run the analysis again.');
        }

        // Load images
        try {
          const imagesRes = await api.getCaseImages(caseId);
          if (imagesRes.images && imagesRes.images.length > 0) {
            setImages(imagesRes.images.map(img => ({
              url: `${api.API_BASE_URL || 'http://127.0.0.1:8081'}/uploads/${caseId}/${img.s3_key ? img.s3_key.split('/').pop() : ''}`
            })));
          } else {
            // Fallback to local
            const localImages = JSON.parse(localStorage.getItem('stellarX_uploaded_images') || '[]');
            setImages(localImages.map(img => ({ url: img.data })));
          }
        } catch {
          const localImages = JSON.parse(localStorage.getItem('stellarX_uploaded_images') || '[]');
          setImages(localImages.map(img => ({ url: img.data })));
        }

        // Load Symptoms
        try {
          const symptomData = await api.getSymptoms(caseId);
          const list = [];
          if (symptomData.redness) list.push('Redness');
          if (symptomData.scaling) list.push('Scaling');
          if (symptomData.ring_shaped) list.push('Ring-shaped lesion');
          if (symptomData.itching) list.push('Itching');
          if (symptomData.pain) list.push('Pain / Tenderness');
          if (symptomData.central_clearing) list.push('Central clearing');
          if (symptomData.nail_changes) list.push('Nail changes');
          
          if (Array.isArray(symptomData.lesion_locations)) {
            list.push(...symptomData.lesion_locations);
          } else if (typeof symptomData.lesion_locations === 'string') {
            list.push(...symptomData.lesion_locations.split(',').map(i => i.trim()).filter(Boolean));
          }
          setSymptoms(list);
        } catch {
          // Fallback
          const localSymptoms = JSON.parse(localStorage.getItem('current_symptoms') || '{}');
          const list = [];
          if (localSymptoms.redness) list.push('Redness');
          if (localSymptoms.scaling) list.push('Scaling');
          if (localSymptoms.ring_shaped) list.push('Ring-shaped lesion');
          if (localSymptoms.itching) list.push('Itching');
          if (localSymptoms.pain) list.push('Pain / Tenderness');
          if (localSymptoms.central_clearing) list.push('Central clearing');
          if (localSymptoms.nail_changes) list.push('Nail changes');
          if (Array.isArray(localSymptoms.lesion_locations)) {
            list.push(...localSymptoms.lesion_locations);
          }
          setSymptoms(list);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [navigate]);

  const handleNewCase = () => {
    localStorage.removeItem('current_case_id');
    localStorage.removeItem('current_symptoms');
    localStorage.removeItem('current_analysis_result');
    localStorage.removeItem('stellarX_uploaded_images');
    navigate('/symptoms');
  };

  const getRankedConditions = () => {
    if (!analysisResult) return [];
    let ranked = analysisResult.ranked_conditions || [];
    ranked = ranked.map(item => {
      let pct = 0;
      if (item.percentage !== undefined) pct = Number(item.percentage);
      else if (item.probability !== undefined) pct = Number(item.probability) * 100;
      return {
        condition: item.condition || 'Unknown',
        percentage: Math.max(0, Math.min(100, Math.round(pct)))
      };
    });
    ranked.sort((a, b) => b.percentage - a.percentage);
    ranked = ranked.slice(0, 3);

    if (ranked.length === 0 && analysisResult.primary_condition) {
      ranked = [{
        condition: analysisResult.primary_condition,
        percentage: Math.round(Number(analysisResult.symptom_confidence || 0) * 100)
      }];
    }
    return ranked;
  };

  const rankedConditions = getRankedConditions();

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

  return (
    <div className="bg-bgGray min-h-screen pb-24">
      {/* Top Nav */}
      <nav className="bg-white/80 backdrop-blur-xl border-b border-slate-100 px-6 md:px-16 py-4 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center space-x-2 cursor-pointer group" onClick={() => navigate('/dashboard')}>
          <div className="w-8 h-8 rounded-lg bg-brand-primary flex items-center justify-center group-hover:scale-105 transition-transform">
            <Layers className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-black tracking-tight text-slate-800">StellarX</span>
        </div>
        <div className="flex items-center">
          <Link to="/dashboard" className="w-10 h-10 bg-slate-50 hover:bg-slate-100 rounded-full flex items-center justify-center text-slate-600 transition-colors border border-slate-200" title="Back to Dashboard">
            <Home className="w-4 h-4" />
          </Link>
        </div>
      </nav>

      <motion.main 
        initial="hidden"
        animate="show"
        variants={containerVariants}
        className="max-w-6xl mx-auto px-6 mt-10 space-y-8"
      >
        <motion.div variants={itemVariants} className="space-y-3 relative">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-brand-primary/10 rounded-full blur-3xl pointer-events-none" />
          <div className="flex items-center justify-center gap-2 text-brand-primary mb-2">
            <Sparkles className="w-5 h-5" />
            <span className="text-xs font-bold uppercase tracking-wider">Diagnostic Engine</span>
          </div>
          <h1 className="text-3xl md:text-5xl font-black text-slate-800 tracking-tight text-center">AI Analysis Results</h1>
          <p className="text-sm md:text-base text-slate-500 font-medium max-w-2xl mx-auto text-center leading-relaxed">
            Symptom-based compatibility percentages generated from the entered clinical information. This tool is for investigational use and should support, not replace, clinical judgment.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start pt-6">
          {/* Left Column (Results) */}
          <motion.div variants={itemVariants} className="bg-white rounded-3xl border border-slate-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-8 lg:col-span-7 space-y-8 relative overflow-hidden">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <h2 className="text-lg font-black text-slate-800 tracking-tight flex items-center gap-2">
                <Activity className="w-5 h-5 text-brand-primary" />
                Predicted Conditions
              </h2>
              <span className="text-[10px] font-bold bg-brand-primary/10 text-brand-primary px-3 py-1 rounded-full uppercase tracking-wider">
                Top Matches
              </span>
            </div>

            <div className="space-y-5">
              {isLoading ? (
                <div className="text-center py-16">
                  <div className="w-12 h-12 border-4 border-brand-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                  <p className="text-sm font-bold text-slate-500">Processing clinical data...</p>
                </div>
              ) : error ? (
                <div className="bg-red-50 rounded-2xl border border-red-100 p-8 text-center shadow-sm">
                  <AlertCircle className="w-10 h-10 text-red-400 mx-auto mb-3" />
                  <p className="text-sm font-bold text-red-600 mb-1">Analysis Error</p>
                  <p className="text-xs font-medium text-red-500">{error}</p>
                </div>
              ) : rankedConditions.length === 0 ? (
                <div className="bg-amber-50 rounded-2xl border border-amber-100 p-8 text-center shadow-sm">
                  <AlertCircle className="w-10 h-10 text-amber-400 mx-auto mb-3" />
                  <p className="text-sm font-bold text-amber-700 mb-1">No Matches Found</p>
                  <p className="text-xs font-medium text-amber-600">The AI model could not confidently predict a condition based on the provided symptoms.</p>
                </div>
              ) : (
                rankedConditions.map((item, index) => {
                  const isFirst = index === 0;
                  let level = 'Low';
                  let badgeClass = 'bg-slate-100 text-slate-500 border-slate-200';
                  let barClass = 'bg-slate-300';
                  let bgClass = 'bg-white border-slate-100';
                  
                  if (item.percentage >= 70) {
                    level = 'High';
                    badgeClass = 'bg-emerald-50 text-emerald-700 border-emerald-200';
                    barClass = 'bg-emerald-500';
                  } else if (item.percentage >= 40) {
                    level = 'Medium';
                    badgeClass = 'bg-amber-50 text-amber-700 border-amber-200';
                    barClass = 'bg-amber-500';
                  }

                  if (isFirst) {
                    bgClass = 'bg-gradient-to-r from-brand-primary/5 to-transparent border-brand-primary/20 shadow-sm';
                    barClass = 'bg-brand-primary';
                  }

                  return (
                    <motion.div 
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.15 }}
                      key={index} 
                      className={`${bgClass} border rounded-2xl p-5 md:p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 relative overflow-hidden`}
                    >
                      {isFirst && <div className="absolute top-0 left-0 w-1.5 h-full bg-brand-primary" />}
                      
                      <div className="flex items-center space-x-5 flex-1">
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${isFirst ? 'bg-brand-primary text-white shadow-md' : 'bg-slate-100 text-slate-400'}`}>
                          <span className="text-xl font-black">
                            #{index + 1}
                          </span>
                        </div>
                        
                        <div className="flex-1 max-w-sm">
                          <span className={`block ${isFirst ? 'text-lg font-black text-slate-900' : 'text-sm font-bold text-slate-800'} tracking-tight capitalize mb-2`}>
                            {item.condition.replace(/_/g, ' ')}
                          </span>
                          <div className={`w-full ${isFirst ? 'bg-brand-primary/10 h-2.5' : 'bg-slate-100 h-2'} rounded-full overflow-hidden`}>
                            <motion.div 
                              initial={{ width: 0 }}
                              animate={{ width: `${item.percentage}%` }}
                              transition={{ duration: 1, delay: 0.5 + (index * 0.1) }}
                              className={`${barClass} h-full rounded-full`}
                            />
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between md:flex-col md:items-end gap-2 md:gap-3 shrink-0 ml-17 md:ml-0">
                        <span className={`text-2xl font-black ${isFirst ? 'text-brand-primary' : 'text-slate-600'}`}>
                          {item.percentage}%
                        </span>
                        <span className={`px-3 py-1 text-[10px] font-bold border rounded-lg ${badgeClass}`}>
                          {level} Confidence
                        </span>
                      </div>
                    </motion.div>
                  );
                })
              )}
            </div>

            <div className="pt-6 border-t border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <span className="block text-[10px] font-black text-slate-400 uppercase tracking-wider">Confidence Thresholds</span>
              <div className="flex flex-wrap items-center gap-4 text-xs font-bold text-slate-600">
                <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-slate-50 border border-slate-100"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>≥ 70%</div>
                <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-slate-50 border border-slate-100"><span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>40% - 69%</div>
                <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-slate-50 border border-slate-100"><span className="w-2.5 h-2.5 rounded-full bg-slate-300"></span>&lt; 40%</div>
              </div>
            </div>
            
            <div className="mt-4 flex items-start gap-3 bg-indigo-50/50 p-4 rounded-xl border border-indigo-100/50">
              <ShieldCheck className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
              <p className="text-[11px] text-indigo-800/70 font-medium leading-relaxed">
                <strong>Clinical Disclaimer:</strong> The AI prediction model analyzes submitted symptom data. It does not replace professional medical diagnosis. Please review all predictions critically.
              </p>
            </div>
          </motion.div>

          {/* Right Column (Input Summary) */}
          <motion.div variants={itemVariants} className="bg-white rounded-3xl border border-slate-100 shadow-sm p-8 lg:col-span-5 space-y-8">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <h2 className="text-lg font-black text-slate-800 tracking-tight flex items-center gap-2">
                <FolderHeart className="w-5 h-5 text-brand-secondary" />
                Case Data
              </h2>
            </div>

            <div className="space-y-4">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">
                <span>Clinical Images</span>
                <span className="text-brand-primary">{images.length}</span>
              </h3>
              
              <div className="border border-slate-200 rounded-2xl bg-slate-50/50 p-4 min-h-[180px] flex flex-col items-center justify-center relative overflow-hidden">
                {images.length > 0 ? (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3 w-full">
                    {images.map((img, i) => (
                      <div key={i} className="aspect-square rounded-xl overflow-hidden border border-slate-200 shadow-sm">
                        <img src={img.url} alt={`Clinical ${i}`} className="w-full h-full object-cover hover:scale-110 transition-transform duration-500" />
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center">
                    <div className="w-12 h-12 bg-white rounded-xl shadow-sm border border-slate-100 flex items-center justify-center mx-auto mb-2 text-slate-300">
                      <Image className="w-5 h-5" />
                    </div>
                    <span className="text-xs font-bold text-slate-400 block">No images attached</span>
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Observed Symptoms</h3>
              <div className="flex flex-wrap gap-2">
                {symptoms.length > 0 ? symptoms.map((sym, i) => (
                  <span key={i} className="px-3 py-1.5 bg-brand-primary/5 text-brand-primary text-xs font-bold rounded-lg border border-brand-primary/20 capitalize shadow-sm">
                    {sym}
                  </span>
                )) : (
                  <div className="w-full p-4 rounded-xl border border-dashed border-slate-200 text-center">
                    <span className="text-xs font-medium text-slate-400">No symptoms recorded</span>
                  </div>
                )}
              </div>
            </div>
            
            {/* Bottom Action Buttons */}
            <div className="pt-6 border-t border-slate-100 space-y-3">
              <button 
                onClick={() => navigate('/dashboard')} 
                className="w-full px-6 py-3.5 bg-brand-primary hover:bg-stellarDark text-white text-sm font-bold rounded-xl transition-all shadow-md hover:shadow-lg flex items-center justify-center gap-2 group"
              >
                <Save className="w-4 h-4 group-hover:-translate-y-0.5 transition-transform" />
                Save & Return to Dashboard
              </button>
              
              <div className="grid grid-cols-2 gap-3">
                <button 
                  onClick={handleNewCase} 
                  className="px-4 py-3 bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 text-xs font-bold rounded-xl transition-all shadow-sm flex items-center justify-center gap-2"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  New Case
                </button>
                <Link 
                  to="/history" 
                  className="px-4 py-3 bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700 text-xs font-bold rounded-xl transition-all shadow-sm flex items-center justify-center gap-2"
                >
                  <FolderHeart className="w-3.5 h-3.5 text-slate-400" />
                  View History
                </Link>
              </div>
            </div>
            
          </motion.div>
        </div>
      </motion.main>
    </div>
  );
}
