import { useState, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Image, UploadCloud, AlertCircle, Clock, Eye as EyeIcon, Activity, Scan, Sparkles, ArrowLeft } from 'lucide-react';
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

  return (
    <div className="p-6 md:p-10 space-y-6 max-w-5xl mx-auto pb-24">
      {/* Title */}
      <div className="space-y-1">
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Enter Observed Symptoms</h1>
        <p className="text-sm text-slate-500 font-medium">Enter the clinical findings to generate weighted symptom compatibility percentages.</p>
      </div>

      {/* Image Upload */}
      <div className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-black text-slate-800 flex items-center gap-2">
            <Image className="w-4 h-4 text-stellarNavy" /> Upload Clinical Images
          </h3>
          <span className="text-xs font-bold text-slate-500 bg-slate-100 px-3 py-1 rounded-full">
            {images.length} / 5
          </span>
        </div>

        <div className="border-2 border-dashed border-slate-200 hover:border-sky-500 rounded-xl bg-slate-50/50 p-6 text-center cursor-pointer transition-colors relative group">
          <input 
            type="file" 
            ref={fileInputRef}
            className="absolute inset-0 opacity-0 cursor-pointer" 
            accept="image/jpeg,image/png,image/webp" 
            multiple 
            onChange={handleImageUpload}
          />
          
          {images.length === 0 ? (
            <div className="space-y-2">
              <div className="w-10 h-10 bg-sky-50 text-stellarNavy rounded-full flex items-center justify-center mx-auto">
                <UploadCloud className="w-5 h-5" />
              </div>
              <p className="text-xs font-bold text-slate-700">
                Drag and drop patient lesion images here, or <span className="text-sky-500">browse</span>
              </p>
              <p className="text-[10px] text-slate-400 font-medium">Supports JPG, PNG and WebP • Maximum 5 images</p>
            </div>
          ) : (
            <div className="flex flex-wrap gap-3 justify-center z-10 relative pointer-events-none">
              {images.map((img, i) => (
                <div key={i} className="relative group pointer-events-auto">
                  <img src={img.data} alt="Upload" className="w-20 h-20 object-cover rounded-lg border border-slate-200 shadow-sm" />
                  <button 
                    type="button" 
                    onClick={() => removeImage(i)}
                    className="absolute -top-2 -right-2 bg-red-500 hover:bg-red-600 transition-colors text-white rounded-full w-5 h-5 flex items-center justify-center text-xs"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
        
        {imageError && (
          <div className="text-xs font-bold text-red-500 flex items-center gap-2">
            <AlertCircle className="w-4 h-4" /> <span>{imageError}</span>
          </div>
        )}
        <p className="text-[10px] text-slate-400">
          The current weighted symptom model does not analyse the image. Images are retained for later image-model integration.
        </p>
      </div>

      {/* Duration and Severity */}
      <div className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-2">
          <h3 className="text-sm font-black text-slate-800 flex items-center gap-2 pb-2 border-b border-slate-100">
            <Clock className="w-4 h-4 text-stellarNavy" /> Duration & Severity
          </h3>
          <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Duration of Symptoms</label>
          <div className="flex gap-3">
            <input 
              type="number" 
              min="1" 
              value={durationValue} 
              onChange={e => setDurationValue(Number(e.target.value))}
              className="w-1/3 px-3 py-2 border border-slate-200 rounded-xl text-sm"
            />
            <select 
              value={durationUnit} 
              onChange={e => setDurationUnit(e.target.value)}
              className="flex-1 px-3 py-2 border border-slate-200 rounded-xl text-sm bg-white"
            >
              <option value="days">Days</option>
              <option value="weeks">Weeks</option>
              <option value="months">Months</option>
            </select>
          </div>
        </div>
        <div className="space-y-2">
          <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider pt-6">Itch Severity</label>
          <div className="flex items-center gap-4 mt-1">
            <span className="text-[10px] font-bold text-slate-400">Mild</span>
            <input 
              type="range" 
              min="1" 
              max="10" 
              value={itchSeverity}
              onChange={e => setItchSeverity(Number(e.target.value))}
              className="flex-1 accent-stellarNavy"
            />
            <span className="text-[10px] font-bold text-slate-400">Severe</span>
            <span className="text-sm font-black text-stellarNavy w-6 text-center">{itchSeverity}</span>
          </div>
        </div>
      </div>

      {/* Appearance and Sensation */}
      <div className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="space-y-4">
          <h3 className="text-sm font-black text-slate-800 flex items-center gap-2 pb-2 border-b border-slate-100">
            <EyeIcon className="w-4 h-4 text-stellarNavy" /> Visual Appearance
          </h3>
          <div className="space-y-3">
            <label className="flex items-center gap-3 cursor-pointer text-xs font-bold text-slate-700">
              <input type="checkbox" checked={redness} onChange={e => setRedness(e.target.checked)} className="w-4 h-4" /> Redness
            </label>
            <label className="flex items-center gap-3 cursor-pointer text-xs font-bold text-slate-700">
              <input type="checkbox" checked={scaling} onChange={e => setScaling(e.target.checked)} className="w-4 h-4" /> Scaling
            </label>
            <label className="flex items-center gap-3 cursor-pointer text-xs font-bold text-slate-700">
              <input type="checkbox" checked={ringShaped} onChange={e => setRingShaped(e.target.checked)} className="w-4 h-4" /> Ring-shaped lesion
            </label>
          </div>
        </div>
        <div className="space-y-4">
          <h3 className="text-sm font-black text-slate-800 flex items-center gap-2 pb-2 border-b border-slate-100">
            <Activity className="w-4 h-4 text-stellarNavy" /> Sensation
          </h3>
          <div className="space-y-3">
            <label className="flex items-center gap-3 cursor-pointer text-xs font-bold text-slate-700">
              <input type="checkbox" checked={itching} onChange={e => setItching(e.target.checked)} className="w-4 h-4" /> Itching
            </label>
            <label className="flex items-center gap-3 cursor-pointer text-xs font-bold text-slate-700">
              <input type="checkbox" checked={pain} onChange={e => setPain(e.target.checked)} className="w-4 h-4" /> Pain / Tenderness
            </label>
          </div>
        </div>
      </div>

      {/* Lesion Characteristics */}
      <div className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6 space-y-4">
        <h3 className="text-sm font-black text-slate-800 flex items-center gap-2 pb-2 border-b border-slate-100">
          <Scan className="w-4 h-4 text-stellarNavy" /> Lesion Characteristics
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-2">
            <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Lesion Size (cm)</label>
            <input 
              type="number" 
              min="0.1" 
              step="0.5" 
              value={lesionSizeCm}
              onChange={e => setLesionSizeCm(Number(e.target.value))}
              className="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm"
            />
          </div>
          <div className="space-y-2">
            <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Lesion Border</label>
            <select 
              value={lesionBorder} 
              onChange={e => setLesionBorder(e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm bg-white"
            >
              <option value="" disabled>Select border...</option>
              <option value="well_defined_raised">Well-defined, raised</option>
              <option value="well_defined">Well-defined</option>
              <option value="ill_defined">Ill-defined, diffuse</option>
              <option value="irregular">Irregular</option>
            </select>
          </div>
          <div className="space-y-2">
            <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Lesion Shape</span>
            <div className="bg-slate-50/50 border border-slate-200 rounded-xl p-3 space-y-2">
              {['circular', 'irregular', 'multiple_lesions'].map(val => (
                <label key={val} className="flex items-center gap-2.5 text-xs font-bold text-slate-700">
                  <input type="radio" name="lesionShape" value={val} checked={lesionShape === val} onChange={e => setLesionShape(e.target.value)} />
                  {val.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </label>
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4 border-t border-slate-100">
          <div className="space-y-2">
            <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Central Clearing</span>
            <div className="bg-slate-50/50 border border-slate-200 rounded-xl p-3 flex gap-6">
              {['yes', 'no'].map(val => (
                <label key={val} className="flex items-center gap-2 text-xs font-bold text-slate-700">
                  <input type="radio" name="centralClearing" value={val} checked={centralClearing === val} onChange={e => setCentralClearing(e.target.value)} />
                  {val.toUpperCase()}
                </label>
              ))}
            </div>
          </div>
          <div className="space-y-2">
            <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Lesion Color</label>
            <select 
              value={lesionColor} 
              onChange={e => setLesionColor(e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm bg-white"
            >
              <option value="" disabled>Select color...</option>
              <option value="red">Red</option>
              <option value="pink">Pink</option>
              <option value="brown">Brown</option>
              <option value="silver_white">Silver/White</option>
              <option value="dark">Dark/Black</option>
            </select>
          </div>
          <div className="space-y-2">
            <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Lesion Location</span>
            <div className="bg-slate-50/50 border border-slate-200 rounded-xl p-3 grid grid-cols-2 gap-2">
              {locationOptions.map(loc => (
                <label key={loc} className="text-xs font-bold">
                  <input 
                    type="checkbox" 
                    checked={lesionLocations.includes(loc)} 
                    onChange={() => toggleLocation(loc)} 
                    className="mr-1.5"
                  />
                  {loc}
                </label>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Additional Signs */}
      <div className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6 space-y-4">
        <h3 className="text-sm font-black text-slate-800 flex items-center gap-2 pb-2 border-b border-slate-100">
          Additional Clinical Signs
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Previous Treatment</label>
            <select 
              value={previousTreatment} 
              onChange={e => setPreviousTreatment(e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm bg-white"
            >
              <option value="none">None</option>
              <option value="topical_steroid">Topical steroid</option>
              <option value="antifungal_cream">Antifungal cream</option>
              <option value="oral_antifungal">Oral antifungal</option>
              <option value="unknown">Unknown</option>
            </select>
          </div>
          <div className="space-y-2">
            <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Nail Changes</span>
            <div className="bg-slate-50/50 border border-slate-200 rounded-xl p-3 flex gap-6">
              {['yes', 'no'].map(val => (
                <label key={val} className="text-xs font-bold">
                  <input type="radio" name="nailChanges" value={val} checked={nailChanges === val} onChange={e => setNailChanges(e.target.value)} className="mr-1.5" />
                  {val.toUpperCase()}
                </label>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Notes */}
      <div className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6 space-y-4">
        <h3 className="text-sm font-black text-slate-800 pb-2 border-b border-slate-100">Additional Notes</h3>
        <textarea 
          value={clinicalNotes}
          onChange={e => setClinicalNotes(e.target.value)}
          rows="4" 
          placeholder="Enter additional observations"
          className="w-full text-xs p-3 rounded-xl border border-slate-200 resize-none focus:outline-none focus:border-stellarNavy"
        ></textarea>
      </div>

      {error && (
        <div className="rounded-xl p-4 text-sm font-bold bg-red-50 text-red-700 border border-red-200">
          {error}
        </div>
      )}

      {/* Buttons */}
      <div className="flex items-center justify-end gap-3 pt-4">
        <Link 
          to="/dashboard"
          className="px-6 py-2.5 bg-white border border-slate-300 text-slate-700 text-xs font-bold rounded-xl hover:bg-slate-50 transition-colors"
        >
          Back
        </Link>
        <button 
          onClick={handleSubmit}
          disabled={isSubmitting}
          className="px-6 py-2.5 bg-stellarNavy hover:bg-stellarDark text-white text-xs font-bold rounded-xl flex items-center gap-2 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
        >
          <span>{isSubmitting ? 'Analysing Symptoms...' : 'Submit for AI Analysis'}</span>
          <Sparkles className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}
