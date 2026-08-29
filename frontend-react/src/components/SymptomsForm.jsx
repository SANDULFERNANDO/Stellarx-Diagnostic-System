import { useState, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Image, UploadCloud, AlertCircle, Clock, Eye as EyeIcon, Activity, Scan, Sparkles, ArrowLeft, HeartPulse, ShieldAlert, CheckCircle2, ChevronRight, FileText, Plus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../services/api';

export default function SymptomsForm() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  // Form State
  const [images, setImages] = useState([]);
  const [durationValue, setDurationValue] = useState(1);
  const [durationUnit, setDurationUnit] = useState('weeks');
  const [itchSeverity, setItchSeverity] = useState(5);
  
  // Checkboxes for visual & sensation
  const [redness, setRedness] = useState(false);
  const [scaling, setScaling] = useState(false);
  const [ringShaped, setRingShaped] = useState(false);
  const [itching, setItching] = useState(false);
  const [pain, setPain] = useState(false);

  // Characteristics
  const [lesionSizeCm, setLesionSizeCm] = useState(2.5);
  const [lesionBorder, setLesionBorder] = useState('');
  const [lesionShape, setLesionShape] = useState('');
  const [centralClearing, setCentralClearing] = useState('');
  const [lesionColor, setLesionColor] = useState('');
  const [lesionLocations, setLesionLocations] = useState([]);

  // Additional
  const [previousTreatment, setPreviousTreatment] = useState('none');
  const [nailChanges, setNailChanges] = useState('');
  const [clinicalNotes, setClinicalNotes] = useState('');

  // UI State
  const [error, setError] = useState('');
  const [imageError, setImageError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Locations array
  const locationOptions = ['Arms', 'Legs', 'Face', 'Hands', 'Feet', 'Scalp', 'Back', 'Neck', 'Chest', 'Abdomen'];

  const toggleLocation = (loc) => {
    setLesionLocations(prev => 
      prev.includes(loc) ? prev.filter(l => l !== loc) : [...prev, loc]
    );
  };

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files);
    if (!files.length) return;
    if (images.length + files.length > 5) {
      setImageError('Maximum 5 images allowed.');
      return;
    }
    setImageError('');

    const newImages = [];
    files.forEach(file => {
      if (!file.type.startsWith('image/')) return;
      const reader = new FileReader();
      reader.onload = (event) => {
        newImages.push({ name: file.name, data: event.target.result });
        if (newImages.length === files.length) {
          setImages(prev => [...prev, ...newImages]);
        }
      };
      reader.readAsDataURL(file);
    });
    
    // reset input
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const removeImage = (index) => {
    setImages(prev => prev.filter((_, i) => i !== index));
    setImageError('');
  };

  const validate = () => {
    if (images.length === 0) {
      setError('An image input is required for AI analysis.');
      return false;
    }

    const hasMajorSymptom = 
      redness || scaling || ringShaped || itching || pain || 
      (centralClearing !== '') || (nailChanges !== '') || 
      !!lesionBorder || !!lesionColor || !!lesionShape;

    if (!hasMajorSymptom) {
      setError('Please select at least one symptom or clinical sign.');
      return false;
    }
    return true;
  };

  const handleSubmit = async () => {
    if (isSubmitting) return;
    setError('');

    if (!validate()) return;
    
    setIsSubmitting(true);

    const symptomsData = {
      redness,
      scaling,
      ring_shaped: ringShaped,
      itching,
      pain,
      duration_value: durationValue,
      duration_unit: durationUnit,
      itch_severity: itchSeverity,
      lesion_size_cm: lesionSizeCm,
      lesion_border: lesionBorder || null,
      lesion_shape: lesionShape || null,
      lesion_color: lesionColor || null,
      lesion_locations: lesionLocations,
      central_clearing: centralClearing === 'yes',
      previous_treatment: previousTreatment,
      nail_changes: nailChanges === 'yes',
      notes: clinicalNotes.trim() || null
    };

    try {
      localStorage.setItem('current_symptoms', JSON.stringify(symptomsData));
      localStorage.setItem('stellarX_uploaded_images', JSON.stringify(images));

      const patientLoc = lesionLocations.length > 0 ? lesionLocations.join(', ') : 'Unknown';
      const newCase = await api.createCase(35, 'male', patientLoc);
      
      if (!newCase || !newCase.case_id) {
        throw new Error('Backend did not return a case ID');
      }
      const caseId = newCase.case_id;
      localStorage.setItem('current_case_id', caseId);

      // Upload Images
      if (images.length > 0) {
        await api.uploadCaseImages(caseId, images);
      }

      await api.saveSymptoms(caseId, symptomsData);
      const analysisResult = await api.runAnalysis(caseId);

      if (!analysisResult || !Array.isArray(analysisResult.ranked_conditions)) {
        throw new Error('Backend returned an invalid analysis result');
      }

      localStorage.setItem('current_analysis_result', JSON.stringify(analysisResult));
      navigate('/result');

    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to complete symptom analysis.');
      setIsSubmitting(false);
    }
  };

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.05 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 24 } }
  };

  return (
    <motion.div 
      initial="hidden"
      animate="show"
      variants={containerVariants}
      className="p-6 md:p-10 space-y-8 max-w-5xl mx-auto pb-32"
    >
      {/* Title Header */}
      <motion.div variants={itemVariants} className="flex flex-col md:flex-row md:items-end justify-between gap-6 bg-white p-8 rounded-3xl shadow-sm border border-slate-100 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-brand-primary/5 to-brand-secondary/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3 pointer-events-none" />
        
        <div className="space-y-3 relative z-10">
          <div className="flex items-center space-x-2 text-brand-secondary">
            <HeartPulse className="w-5 h-5" />
            <span className="text-xs font-bold uppercase tracking-wider">Clinical Intake</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-black text-slate-800 tracking-tight">New Diagnostic Case</h1>
          <p className="text-sm md:text-base text-slate-500 font-medium max-w-xl leading-relaxed">
            Enter the patient's observed symptoms, medical history, and upload clinical images to begin AI analysis.
          </p>
        </div>
        
        <div className="relative z-10 shrink-0 flex gap-3">
          <Link 
            to="/dashboard" 
            className="px-5 py-2.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 hover:border-slate-300 rounded-xl text-sm font-bold text-slate-700 shadow-sm transition-all flex items-center justify-center gap-2 group"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" /> Cancel
          </Link>
        </div>
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column (Main Form) */}
        <div className="lg:col-span-8 space-y-8">
          
          {/* Image Upload */}
          <motion.div variants={itemVariants} className="bg-white rounded-3xl border border-slate-100 shadow-sm p-8 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-32 h-32 bg-sky-50 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 group-hover:scale-110 transition-transform duration-500" />
            
            <div className="flex items-center justify-between mb-6 relative z-10">
              <h3 className="text-base font-black text-slate-800 flex items-center gap-2.5">
                <div className="w-8 h-8 bg-sky-50 rounded-lg flex items-center justify-center">
                  <Image className="w-4 h-4 text-brand-primary" />
                </div>
                Clinical Images <span className="text-red-500">*</span>
              </h3>
              <span className={`text-xs font-bold px-3 py-1.5 rounded-full flex items-center gap-1.5 ${images.length > 0 ? 'bg-sky-50 text-brand-primary' : 'bg-slate-100 text-slate-500'}`}>
                {images.length > 0 && <CheckCircle2 className="w-3.5 h-3.5" />}
                {images.length} / 5 Uploaded
              </span>
            </div>

            <div className="border-2 border-dashed border-slate-200 hover:border-brand-primary rounded-2xl bg-slate-50/50 p-8 text-center cursor-pointer transition-colors relative group/dropzone z-10">
              <input 
                type="file" 
                ref={fileInputRef}
                className="absolute inset-0 opacity-0 cursor-pointer z-20" 
                accept="image/jpeg,image/png,image/webp" 
                multiple 
                onChange={handleImageUpload}
              />
              
              {images.length === 0 ? (
                <div className="space-y-3 pointer-events-none">
                  <div className="w-16 h-16 bg-white shadow-sm border border-slate-100 text-brand-primary rounded-2xl flex items-center justify-center mx-auto group-hover/dropzone:scale-110 group-hover/dropzone:-translate-y-1 transition-all duration-300">
                    <UploadCloud className="w-8 h-8" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-slate-700">
                      Drag & drop clinical images here
                    </p>
                    <p className="text-xs font-medium text-brand-primary mt-1">or click to browse files</p>
                  </div>
                  <div className="pt-2 flex items-center justify-center gap-4 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    <span>JPEG, PNG, WebP</span>
                    <span className="w-1 h-1 rounded-full bg-slate-300"></span>
                    <span>Max 5 images</span>
                  </div>
                </div>
              ) : (
                <div className="flex flex-wrap gap-4 justify-center z-30 relative">
                  <AnimatePresence>
                    {images.map((img, i) => (
                      <motion.div 
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.8 }}
                        key={i} 
                        className="relative group/img pointer-events-auto"
                      >
                        <img src={img.data} alt="Upload" className="w-24 h-24 object-cover rounded-xl border border-slate-200 shadow-sm" />
                        <div className="absolute inset-0 bg-black/40 rounded-xl opacity-0 group-hover/img:opacity-100 transition-opacity flex items-center justify-center" />
                        <button 
                          type="button" 
                          onClick={(e) => { e.preventDefault(); e.stopPropagation(); removeImage(i); }}
                          className="absolute -top-2 -right-2 bg-white text-slate-700 hover:text-red-500 hover:scale-110 shadow-md border border-slate-100 transition-all rounded-full w-7 h-7 flex items-center justify-center text-sm font-bold z-40"
                        >
                          ×
                        </button>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                  
                  {images.length < 5 && (
                    <div className="w-24 h-24 rounded-xl border-2 border-dashed border-slate-300 flex flex-col items-center justify-center text-slate-400 hover:text-brand-primary hover:border-brand-primary hover:bg-white transition-colors cursor-pointer pointer-events-auto">
                      <Plus className="w-6 h-6 mb-1" />
                      <span className="text-[10px] font-bold uppercase tracking-wider">Add More</span>
                    </div>
                  )}
                </div>
              )}
            </div>
            
            <AnimatePresence>
              {imageError && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className="mt-4">
                  <div className="text-xs font-bold text-red-500 bg-red-50 border border-red-100 px-4 py-3 rounded-xl flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 shrink-0" /> <span>{imageError}</span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            
            <div className="mt-4 flex items-start gap-2 bg-slate-50 p-4 rounded-xl border border-slate-100">
              <ShieldAlert className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
              <p className="text-[11px] text-slate-500 font-medium leading-relaxed">
                Images are securely stored for documentation purposes. The current AI model primarily analyzes structural text data (symptoms). Image analysis models are currently in beta integration.
              </p>
            </div>
          </motion.div>

          {/* Lesion Characteristics */}
          <motion.div variants={itemVariants} className="bg-white rounded-3xl border border-slate-100 shadow-sm p-8 space-y-6 relative overflow-hidden">
            <h3 className="text-base font-black text-slate-800 flex items-center gap-2.5 pb-4 border-b border-slate-100">
              <div className="w-8 h-8 bg-indigo-50 rounded-lg flex items-center justify-center">
                <Scan className="w-4 h-4 text-indigo-500" />
              </div>
              Lesion Characteristics
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider">Lesion Size (cm)</label>
                <div className="relative group">
                  <input 
                    type="number" 
                    min="0.1" 
                    step="0.5" 
                    value={lesionSizeCm}
                    onChange={e => setLesionSizeCm(Number(e.target.value))}
                    className="w-full pl-4 pr-10 py-3 bg-slate-50 border border-slate-200 focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 rounded-xl text-sm font-medium text-slate-800 outline-none transition-all"
                  />
                  <span className="absolute right-4 top-3.5 text-xs font-bold text-slate-400">cm</span>
                </div>
              </div>
              
              <div className="space-y-2">
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider">Lesion Border</label>
                <select 
                  value={lesionBorder} 
                  onChange={e => setLesionBorder(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 rounded-xl text-sm font-medium text-slate-800 outline-none transition-all cursor-pointer appearance-none"
                >
                  <option value="" disabled>Select border type...</option>
                  <option value="well_defined_raised">Well-defined, raised</option>
                  <option value="well_defined">Well-defined, flat</option>
                  <option value="ill_defined">Ill-defined, diffuse</option>
                  <option value="irregular">Irregular / jagged</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider">Lesion Color</label>
                <select 
                  value={lesionColor} 
                  onChange={e => setLesionColor(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 rounded-xl text-sm font-medium text-slate-800 outline-none transition-all cursor-pointer appearance-none"
                >
                  <option value="" disabled>Select predominant color...</option>
                  <option value="red">Erythematous (Red)</option>
                  <option value="pink">Pink / Salmon</option>
                  <option value="brown">Hyperpigmented (Brown)</option>
                  <option value="silver_white">Silver / White</option>
                  <option value="dark">Dark / Black</option>
                </select>
              </div>

              <div className="space-y-2">
                <span className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Lesion Shape</span>
                <div className="flex gap-2 p-1.5 bg-slate-50 border border-slate-200 rounded-xl">
                  {[
                    { val: 'circular', label: 'Circular' },
                    { val: 'irregular', label: 'Irregular' },
                    { val: 'multiple_lesions', label: 'Multiple' }
                  ].map(({ val, label }) => (
                    <label 
                      key={val} 
                      className={`flex-1 flex justify-center items-center py-2 px-1 text-xs font-bold rounded-lg cursor-pointer transition-all ${lesionShape === val ? 'bg-white text-brand-primary shadow-sm border border-slate-100' : 'text-slate-500 hover:bg-slate-100'}`}
                    >
                      <input type="radio" name="lesionShape" className="hidden" value={val} checked={lesionShape === val} onChange={e => setLesionShape(e.target.value)} />
                      {label}
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className="pt-6 border-t border-slate-100">
              <span className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Anatomical Locations</span>
              <div className="flex flex-wrap gap-2">
                {locationOptions.map(loc => {
                  const isSelected = lesionLocations.includes(loc);
                  return (
                    <label 
                      key={loc} 
                      className={`inline-flex items-center px-4 py-2 rounded-xl text-xs font-bold cursor-pointer transition-all border ${isSelected ? 'bg-brand-primary text-white border-brand-primary shadow-sm shadow-brand-primary/20' : 'bg-white text-slate-600 border-slate-200 hover:border-brand-primary/50 hover:bg-slate-50'}`}
                    >
                      <input 
                        type="checkbox" 
                        className="hidden"
                        checked={isSelected} 
                        onChange={() => toggleLocation(loc)} 
                      />
                      {loc}
                    </label>
                  );
                })}
              </div>
            </div>
          </motion.div>

          {/* Appearance & Sensation */}
          <motion.div variants={itemVariants} className="bg-white rounded-3xl border border-slate-100 shadow-sm p-8 space-y-6">
            <h3 className="text-base font-black text-slate-800 flex items-center gap-2.5 pb-4 border-b border-slate-100">
              <div className="w-8 h-8 bg-emerald-50 rounded-lg flex items-center justify-center">
                <EyeIcon className="w-4 h-4 text-emerald-500" />
              </div>
              Visual & Sensatory Presentation
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <span className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Visual Markers</span>
                
                {[
                  { state: redness, setter: setRedness, label: 'Erythema (Redness)', desc: 'Noticeable redness around or on the lesion' },
                  { state: scaling, setter: setScaling, label: 'Scaling / Flaking', desc: 'Dry, flaky, or peeling skin' },
                  { state: ringShaped, setter: setRingShaped, label: 'Annular (Ring-shaped)', desc: 'Clear center with active border' },
                ].map(({ state, setter, label, desc }, i) => (
                  <label key={i} className={`flex items-start gap-3 p-3 rounded-xl border transition-all cursor-pointer ${state ? 'bg-brand-primary/5 border-brand-primary/30' : 'bg-white border-slate-200 hover:border-slate-300'}`}>
                    <div className="relative flex items-center justify-center mt-0.5">
                      <input type="checkbox" className="peer appearance-none w-5 h-5 border-2 border-slate-300 rounded focus:ring-4 focus:ring-brand-primary/20 checked:border-brand-primary checked:bg-brand-primary transition-colors cursor-pointer" checked={state} onChange={e => setter(e.target.checked)} />
                      <CheckCircle2 className="w-3.5 h-3.5 text-white absolute opacity-0 peer-checked:opacity-100 pointer-events-none" />
                    </div>
                    <div>
                      <span className={`block text-sm font-bold ${state ? 'text-brand-primary' : 'text-slate-700'}`}>{label}</span>
                      <span className="block text-xs font-medium text-slate-500">{desc}</span>
                    </div>
                  </label>
                ))}
              </div>
              
              <div className="space-y-3">
                <span className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Sensatory Markers</span>
                
                {[
                  { state: itching, setter: setItching, label: 'Pruritus (Itching)', desc: 'Patient reports urge to scratch' },
                  { state: pain, setter: setPain, label: 'Pain / Tenderness', desc: 'Lesion is painful to touch or at rest' },
                ].map(({ state, setter, label, desc }, i) => (
                  <label key={i} className={`flex items-start gap-3 p-3 rounded-xl border transition-all cursor-pointer ${state ? 'bg-brand-primary/5 border-brand-primary/30' : 'bg-white border-slate-200 hover:border-slate-300'}`}>
                    <div className="relative flex items-center justify-center mt-0.5">
                      <input type="checkbox" className="peer appearance-none w-5 h-5 border-2 border-slate-300 rounded focus:ring-4 focus:ring-brand-primary/20 checked:border-brand-primary checked:bg-brand-primary transition-colors cursor-pointer" checked={state} onChange={e => setter(e.target.checked)} />
                      <CheckCircle2 className="w-3.5 h-3.5 text-white absolute opacity-0 peer-checked:opacity-100 pointer-events-none" />
                    </div>
                    <div>
                      <span className={`block text-sm font-bold ${state ? 'text-brand-primary' : 'text-slate-700'}`}>{label}</span>
                      <span className="block text-xs font-medium text-slate-500">{desc}</span>
                    </div>
                  </label>
                ))}
                
                <div className="pt-2">
                  <span className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Central Clearing</span>
                  <div className="flex gap-2 p-1.5 bg-slate-50 border border-slate-200 rounded-xl">
                    {[
                      { val: 'yes', label: 'Present' },
                      { val: 'no', label: 'Absent' },
                    ].map(({ val, label }) => (
                      <label 
                        key={val} 
                        className={`flex-1 flex justify-center items-center py-2 px-1 text-xs font-bold rounded-lg cursor-pointer transition-all ${centralClearing === val ? 'bg-white text-brand-primary shadow-sm border border-slate-100' : 'text-slate-500 hover:bg-slate-100'}`}
                      >
                        <input type="radio" name="centralClearing" className="hidden" value={val} checked={centralClearing === val} onChange={e => setCentralClearing(e.target.value)} />
                        {label}
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Right Column (Sidebar inputs & submit) */}
        <div className="lg:col-span-4 space-y-6">
          
          <motion.div variants={itemVariants} className="bg-white rounded-3xl border border-slate-100 shadow-sm p-6 space-y-6">
            <h3 className="text-sm font-black text-slate-800 flex items-center gap-2 pb-3 border-b border-slate-100">
              <Clock className="w-4 h-4 text-brand-secondary" /> Duration & Severity
            </h3>
            
            <div className="space-y-3">
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider">Onset Duration</label>
              <div className="flex gap-2">
                <input 
                  type="number" 
                  min="1" 
                  value={durationValue} 
                  onChange={e => setDurationValue(Number(e.target.value))}
                  className="w-20 px-3 py-2.5 bg-slate-50 border border-slate-200 focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 rounded-xl text-sm font-medium text-slate-800 outline-none transition-all text-center"
                />
                <select 
                  value={durationUnit} 
                  onChange={e => setDurationUnit(e.target.value)}
                  className="flex-1 px-3 py-2.5 bg-slate-50 border border-slate-200 focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 rounded-xl text-sm font-medium text-slate-800 outline-none transition-all cursor-pointer appearance-none"
                >
                  <option value="days">Days</option>
                  <option value="weeks">Weeks</option>
                  <option value="months">Months</option>
                  <option value="years">Years</option>
                </select>
              </div>
            </div>

            <div className="space-y-3 pt-2">
              <div className="flex justify-between items-end">
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider">Itch Severity</label>
                <span className="text-lg font-black text-brand-primary">{itchSeverity}<span className="text-xs text-slate-400 font-bold">/10</span></span>
              </div>
              <input 
                type="range" 
                min="0" 
                max="10" 
                value={itchSeverity}
                onChange={e => setItchSeverity(Number(e.target.value))}
                className="w-full accent-brand-primary h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-[10px] font-bold text-slate-400 uppercase">
                <span>None (0)</span>
                <span>Severe (10)</span>
              </div>
            </div>
          </motion.div>

          <motion.div variants={itemVariants} className="bg-white rounded-3xl border border-slate-100 shadow-sm p-6 space-y-6">
            <h3 className="text-sm font-black text-slate-800 flex items-center gap-2 pb-3 border-b border-slate-100">
              <Activity className="w-4 h-4 text-amber-500" /> Additional Details
            </h3>
            
            <div className="space-y-3">
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider">Previous Treatment</label>
              <select 
                value={previousTreatment} 
                onChange={e => setPreviousTreatment(e.target.value)}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 rounded-xl text-sm font-medium text-slate-800 outline-none transition-all cursor-pointer appearance-none"
              >
                <option value="none">None / Naive</option>
                <option value="topical_steroid">Topical Corticosteroid</option>
                <option value="antifungal_cream">Topical Antifungal</option>
                <option value="oral_antifungal">Oral Antifungal</option>
                <option value="antibiotic">Antibiotics</option>
                <option value="unknown">Unknown</option>
              </select>
            </div>

            <div className="space-y-3">
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider">Nail Involvement</label>
              <div className="flex gap-2 p-1.5 bg-slate-50 border border-slate-200 rounded-xl">
                {[
                  { val: 'yes', label: 'Present' },
                  { val: 'no', label: 'Absent' },
                ].map(({ val, label }) => (
                  <label 
                    key={val} 
                    className={`flex-1 flex justify-center items-center py-2 px-1 text-xs font-bold rounded-lg cursor-pointer transition-all ${nailChanges === val ? 'bg-white text-brand-primary shadow-sm border border-slate-100' : 'text-slate-500 hover:bg-slate-100'}`}
                  >
                    <input type="radio" name="nailChanges" className="hidden" value={val} checked={nailChanges === val} onChange={e => setNailChanges(e.target.value)} />
                    {label}
                  </label>
                ))}
              </div>
            </div>

            <div className="space-y-3 pt-2">
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5" /> Clinical Notes
              </label>
              <textarea 
                value={clinicalNotes}
                onChange={e => setClinicalNotes(e.target.value)}
                rows="4" 
                placeholder="Enter additional observations or patient history..."
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 focus:border-brand-primary focus:ring-4 focus:ring-brand-primary/10 rounded-xl text-sm font-medium text-slate-800 outline-none transition-all resize-none"
              ></textarea>
            </div>
          </motion.div>

          <AnimatePresence>
            {error && (
              <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                <div className="bg-red-50 border border-red-200 p-4 rounded-2xl flex items-start gap-3 shadow-sm">
                  <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                  <p className="text-sm font-bold text-red-700 leading-relaxed">{error}</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Action Buttons (Sticky on mobile, relative on desktop) */}
          <motion.div variants={itemVariants} className="fixed bottom-0 left-0 right-0 p-4 bg-white/80 backdrop-blur-xl border-t border-slate-200 z-50 lg:relative lg:p-0 lg:bg-transparent lg:backdrop-blur-none lg:border-t-0 lg:z-auto shadow-[0_-10px_40px_-15px_rgba(0,0,0,0.1)] lg:shadow-none flex items-center justify-end gap-3">
            <button 
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="w-full lg:w-auto px-8 py-4 bg-brand-primary hover:bg-stellarDark text-white text-sm font-bold rounded-2xl flex items-center justify-center gap-2 transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-70 disabled:pointer-events-none group"
            >
              <span>{isSubmitting ? 'Analyzing Data...' : 'Submit for AI Analysis'}</span>
              {!isSubmitting && <Sparkles className="w-4 h-4 group-hover:rotate-12 transition-transform" />}
              {isSubmitting && <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>}
            </button>
          </motion.div>
          
        </div>
      </div>
    </motion.div>
  );
}
