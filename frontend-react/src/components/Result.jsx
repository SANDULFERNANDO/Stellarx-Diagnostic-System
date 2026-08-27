import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Layers, Home } from 'lucide-react';
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

  return (
    <div className="bg-bgGray min-h-screen pb-24">
      {/* Top Nav */}
      <nav className="bg-white border-b border-slate-100 px-6 md:px-16 py-4 flex items-center justify-between shadow-sm">
        <div className="flex items-center space-x-2 cursor-pointer" onClick={() => navigate('/dashboard')}>
          <Layers className="w-6 h-6 text-stellarNavy" />
          <span className="text-xl font-black tracking-tight text-stellarNavy">StellarX</span>
        </div>
        <div className="flex items-center">
          <Link to="/dashboard" className="w-8 h-8 bg-slate-100 hover:bg-slate-200 rounded-full flex items-center justify-center text-slate-600 transition-colors" title="Back to Dashboard">
            <Home className="w-4 h-4" />
          </Link>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 mt-10 space-y-6">
        <div className="space-y-1">
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">AI Analysis Results</h1>
          <p className="text-sm text-slate-500 font-medium">
            Symptom-based compatibility percentages generated from the entered clinical information.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column */}
          <div className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6 lg:col-span-7 space-y-6">
            <div>
              <h3 className="text-[11px] font-black text-slate-400 uppercase tracking-wider">Predicted Conditions</h3>
            </div>

            <div className="space-y-4">
              {isLoading ? (
                <div className="text-sm font-semibold text-slate-400 py-6 text-center">Loading analysis results...</div>
              ) : error ? (
                <div className="border border-red-100 bg-red-50 rounded-xl p-5">
                  <p className="text-sm font-bold text-red-600">{error}</p>
                </div>
              ) : rankedConditions.length === 0 ? (
                <div className="border border-amber-100 bg-amber-50 rounded-xl p-5">
                  <p className="text-sm font-bold text-amber-700">No ranked conditions were returned.</p>
                </div>
              ) : (
                rankedConditions.map((item, index) => {
                  const isFirst = index === 0;
                  let level = 'Low';
                  let badgeClass = 'bg-slate-100 text-slate-500';
                  if (item.percentage >= 70) {
                    level = 'High';
                    badgeClass = 'bg-emerald-100 text-emerald-800';
                  } else if (item.percentage >= 40) {
                    level = 'Medium';
                    badgeClass = 'bg-amber-100 text-amber-800';
                  }

                  return (
                    <div key={index} className={`${isFirst ? 'bg-[#f0f7ff] border-blue-100/70' : 'bg-white border-slate-100'} border rounded-xl p-4 flex items-center justify-between`}>
                      <div className="flex items-center space-x-4 flex-1">
                        <span className={`${isFirst ? 'text-2xl text-blue-600/40' : 'text-xl text-slate-300'} font-black`}>
                          {index + 1}
                        </span>
                        <div className="flex-1 max-w-xs">
                          <span className={`block ${isFirst ? 'text-sm font-black text-slate-900' : 'text-xs font-bold text-slate-800'} tracking-tight capitalize`}>
                            {item.condition.replace(/_/g, ' ')}
                          </span>
                          <div className={`w-full ${isFirst ? 'bg-blue-100 h-2' : 'bg-slate-100 h-1.5'} rounded-full mt-1`}>
                            <div className={`${isFirst ? 'bg-blue-600 h-2' : 'bg-slate-400 h-1.5'} rounded-full transition-all duration-500`} style={{ width: `${item.percentage}%` }}></div>
                          </div>
                          <span className={`${isFirst ? 'text-[10px] text-blue-600 mt-1' : 'text-[9px] text-slate-400 mt-0.5'} font-bold block`}>
                            {isFirst ? `${item.percentage}% Match` : `${item.percentage}%`}
                          </span>
                        </div>
                      </div>
                      <span className={`px-3 py-1 text-[10px] font-black ${badgeClass} rounded-lg`}>
                        {level}
                      </span>
                    </div>
                  );
                })
              )}
            </div>

            <div className="pt-4 border-t border-slate-100 space-y-2">
              <span className="block text-[10px] font-black text-slate-400 uppercase tracking-wider">Confidence Legend</span>
              <div className="flex flex-wrap items-center gap-5 text-[11px] font-bold text-slate-600">
                <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>High: ≥ 70%</div>
                <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>Medium: 40% - 69%</div>
                <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-slate-400"></span>Low: &lt; 40%</div>
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6 lg:col-span-5 space-y-6">
            <div><h2 className="text-base font-black text-slate-900 tracking-tight">Input Summary</h2></div>

            <div className="space-y-2">
              <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">1. Uploaded Clinical Images</span>
              <div className="border border-slate-200 rounded-xl bg-slate-50/50 p-2 min-h-[220px] flex items-center justify-center relative overflow-hidden">
                {images.length > 0 ? (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2 w-full">
                    {images.map((img, i) => (
                      <img key={i} src={img.url} alt={`Clinical ${i}`} className="w-full h-32 object-cover rounded-lg border border-slate-200 shadow-sm" />
                    ))}
                  </div>
                ) : (
                  <div className="text-xs font-bold text-slate-400 tracking-wide block">No images uploaded</div>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">2. Selected Symptoms</span>
              <div className="flex flex-wrap gap-2 pt-1">
                {symptoms.length > 0 ? symptoms.map((sym, i) => (
                  <span key={i} className="px-3 py-1.5 bg-slate-100 text-slate-600 text-[10px] font-bold rounded-lg border border-slate-200/60 capitalize">
                    {sym}
                  </span>
                )) : (
                  <span className="text-xs text-slate-400">No symptoms recorded</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Buttons */}
        <div className="flex items-center justify-end gap-3 pt-6">
          <Link to="/history" className="px-6 py-2.5 bg-slate-50 hover:bg-slate-100 border border-slate-300 text-slate-700 text-xs font-bold rounded-xl transition-all shadow-sm">
            View History
          </Link>
          <button onClick={handleNewCase} className="px-6 py-2.5 bg-white hover:bg-slate-50 border border-slate-300 text-stellarNavy text-xs font-bold rounded-xl transition-all shadow-sm">
            New Case
          </button>
          <Link to="/dashboard" className="px-6 py-2.5 bg-stellarNavy hover:bg-stellarDark text-white text-xs font-bold rounded-xl transition-all shadow-sm">
            Save Case
          </Link>
        </div>
      </main>
    </div>
  );
}
