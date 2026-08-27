"""
Symptom Scoring Module for Tinea Infection, Leishmaniasis, and Eczema.

Provides a weighted symptom decision support system based on dermatological guidelines.
"""
import logging
import math
import json
from typing import Any, Dict, List, Union

# Configure logging
logger = logging.getLogger(__name__)

# Clinical weights dictionary
DISEASE_WEIGHTS = {
    "Tinea Infection": {
        "ring_shaped": 8.0,
        "central_clearing": 6.0,
        "border_well_defined_raised": 5.0,
        "shape_circular": 6.0,
        "scaling": 3.5,
        "itching": 2.5,
        "redness": 2.0,
        "border_well_defined": 3.0,
        "shape_multiple": 0.5,
        "pain": -0.5,
        "color_red": 1.0,       # ✅ ADDED: Tinea can present with redness
        "color_dark": -0.5,
        "color_brown": 0.5,
        "color_silver_white": 0.5,
        "location_arms": 0.8,
        "location_legs": 0.8,
        "location_feet": 0.8,
        "location_face": 0.4,
        "location_hands": 0.4,
        "location_scalp": 0.4,
        "location_back": 0.4,
        "location_neck": 0.4,
        "location_chest": 0.4,
        "location_abdomen": 0.4,
        "nail_changes": 0.5,
        "treatment_antifungal_cream": 1.0,
        "treatment_oral_antifungal": 1.0,
        "treatment_topical_steroid": 0.0,
    },
    "Leishmaniasis": {
        "pain": 5.0,
        "color_dark": 5.0,
        "shape_irregular": 4.5,
        "border_ill_defined": 3.5,
        "color_brown": 3.0,
        "shape_multiple": 2.0,
        "border_well_defined": 2.0,
        "redness": 2.5,
        "border_well_defined_raised": 1.5,
        "scaling": 1.0,
        "color_red": 1.5,       # ✅ ADDED: ulcerative Leishmania often presents red
        "itching": -1.0,
        "ring_shaped": -2.0,
        "central_clearing": -2.0,
        "location_arms": 1.0,
        "location_legs": 1.0,
        "location_hands": 1.0,
        "location_feet": 1.0,
        "location_face": 0.2,
        "location_scalp": 3.0,
        "location_back": 1.0,
        "location_chest": 0.5,
        "location_abdomen": 0.5,
        "location_neck": 0.5,
        "treatment_topical_steroid": -1.0,
        "treatment_antifungal_cream": -0.5,
        "treatment_oral_antifungal": -0.5,
        "nail_changes": 0.0,
    },
    "Eczema": {
        "itching": 6.0,
        "redness": 4.0,
        "border_ill_defined": 4.0,
        "shape_irregular": 3.0,
        "scaling": 3.0,
        "shape_multiple": 2.0,
        "color_pink": 2.0,
        "color_silver_white": 2.0,
        "color_red": 1.5,       # ✅ ADDED: Eczema frequently presents as red/inflamed
        "location_hands": 2.0,
        "location_arms": 1.5,
        "location_legs": 1.5,
        "color_brown": 1.0,
        "location_face": 1.0,
        "location_neck": 1.5,
        "location_back": 0.5,
        "location_chest": 0.5,
        "location_abdomen": 0.5,
        "location_feet": 1.0,
        "location_scalp": 0.5,
        "pain": 0.5,
        "border_well_defined_raised": -1.5,
        "ring_shaped": -2.0,
        "central_clearing": -2.0,
        "shape_circular": -0.5,
        "treatment_topical_steroid": 2.0,
        "treatment_antifungal_cream": -0.5,
        "treatment_oral_antifungal": -0.5,
        "nail_changes": 0.5,
    }
}

def _to_dict(symptoms: Any) -> Dict[str, Any]:
    """Safely convert SQLAlchemy model or Pydantic model to a dictionary."""
    if isinstance(symptoms, dict):
        return symptoms
    if hasattr(symptoms, "__dict__"):
        data = symptoms.__dict__.copy()
        data.pop("_sa_instance_state", None)  # Remove SQLAlchemy internal state
        return data
    if hasattr(symptoms, "model_dump"): # Pydantic v2
        return symptoms.model_dump()
    if hasattr(symptoms, "dict"): # Pydantic v1
        return symptoms.dict()
    return {}

def _normalize_value(value: Any) -> str | Any:
    """
    Normalize a categorical string value for lookup-map comparison.

    Converts to lowercase, strips whitespace, and replaces underscores with
    spaces so that HTML option values like ``well_defined_raised`` match the
    same key as a human-readable label.
    """
    if isinstance(value, str):
        return value.lower().strip().replace("_", " ")
    return value

def _parse_locations(locations: Any) -> List[str]:
    """Safely parse lesion locations which could be a list, JSON string, or comma-separated string."""
    if not locations:
        return []
    if isinstance(locations, list):
        return locations
    if isinstance(locations, str):
        try:
            parsed = json.loads(locations)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass
        return [loc.strip() for loc in locations.split(',') if loc.strip()]
    return []

def _map_dropdown(value: str, mapping: Dict[str, str]) -> str:
    """Map a normalized dropdown value to its corresponding feature key."""
    return mapping.get(value, value)

def _selected_features(symptoms_dict: Dict[str, Any]) -> List[str]:
    """Extract a list of features that are considered 'selected' or 'active'."""
    features = []
    
    # Checkboxes and booleans (ensure safe casting from 1/0 to bool)
    if bool(symptoms_dict.get("redness")): features.append("redness")
    if bool(symptoms_dict.get("scaling")): features.append("scaling")
    if bool(symptoms_dict.get("ring_shaped")): features.append("ring_shaped")
    if bool(symptoms_dict.get("itching")): features.append("itching")
    if bool(symptoms_dict.get("pain")): features.append("pain")
    if bool(symptoms_dict.get("central_clearing")): features.append("central_clearing")
    if bool(symptoms_dict.get("nail_changes")): features.append("nail_changes")
    
    # ------------------------------------------------------------------ #
    # Dropdown / Categorical Mappings                                      #
    #                                                                      #
    # Keys must match EXACTLY what _normalize_value() produces from the   #
    # raw HTML option value (lowercased + underscores → spaces).           #
    #                                                                      #
    # HTML option value → _normalize_value() output → map key             #
    # ─────────────────────────────────────────────────────────────────── #
    # "well_defined_raised" → "well defined raised"                        #
    # "well_defined"        → "well defined"                               #
    # "ill_defined"         → "ill defined"          (no "diffuse" suffix) #
    # "multiple_lesions"    → "multiple lesions"                           #
    # "silver_white"        → "silver white"         (no slash)            #
    # "dark"                → "dark"                                       #
    # "topical_steroid"     → "topical steroid"                            #
    # "antifungal_cream"    → "antifungal cream"                           #
    # "oral_antifungal"     → "oral antifungal"                            #
    # ------------------------------------------------------------------ #

    border_map = {
        "well defined raised": "border_well_defined_raised",  # ✅ FIXED
        "well defined":        "border_well_defined",          # ✅ FIXED
        "ill defined":         "border_ill_defined",           # ✅ FIXED (was "ill-defined diffuse")
        "irregular":           "border_irregular",             # used in special rules, no base weight
    }

    shape_map = {
        "circular":        "shape_circular",
        "irregular":       "shape_irregular",
        "multiple lesions": "shape_multiple",  # ✅ FIXED (was "multiple lesions" but HTML sent "multiple_lesions")
    }

    color_map = {
        "red":         "color_red",
        "pink":        "color_pink",
        "brown":       "color_brown",
        "silver white": "color_silver_white",  # ✅ FIXED (was "silver/white", HTML sends "silver_white")
        "dark":        "color_dark",            # ✅ FIXED (was "dark/black", HTML sends "dark")
    }

    treatment_map = {
        "topical steroid":   "treatment_topical_steroid",    # ✅ FIXED (HTML sends "topical_steroid")
        "antifungal cream":  "treatment_antifungal_cream",   # ✅ FIXED
        "oral antifungal":   "treatment_oral_antifungal",    # ✅ FIXED
        "none":              None,   # explicit None means skip
        "unknown":           None,
    }

    border = _normalize_value(symptoms_dict.get("lesion_border"))
    if border and border in border_map:
        feature_key = border_map[border]
        if feature_key:  # skip None entries
            features.append(feature_key)

    shape = _normalize_value(symptoms_dict.get("lesion_shape"))
    if shape and shape in shape_map:
        feature_key = shape_map[shape]
        if feature_key:
            features.append(feature_key)

    color = _normalize_value(symptoms_dict.get("lesion_color"))
    if color and color in color_map:
        feature_key = color_map[color]
        if feature_key:
            features.append(feature_key)

    treatment = _normalize_value(symptoms_dict.get("previous_treatment"))
    if treatment and treatment in treatment_map:
        feature_key = treatment_map[treatment]
        if feature_key:
            features.append(feature_key)
    elif treatment and treatment not in treatment_map:
        # Fallback: pass through normalised value prefixed with "treatment_"
        fallback_key = f"treatment_{treatment.replace(' ', '_')}"
        if fallback_key in next(iter(DISEASE_WEIGHTS.values()), {}):
            features.append(fallback_key)

    locations = _parse_locations(symptoms_dict.get("lesion_locations"))
    for loc in locations:
        # _normalize_value lowercases and converts underscores→spaces;
        # we then replace spaces back to underscores for the feature key.
        loc_normalized = _normalize_value(loc).replace(" ", "_")
        features.append(f"location_{loc_normalized}")

    return features

def _apply_numeric_scores(scores: Dict[str, float], symptoms_dict: Dict[str, Any]) -> None:
    """Apply scoring adjustments based on numeric inputs (severity, duration, size)."""
    # RULE 5: Itch Severity Scaling
    severity = symptoms_dict.get("itch_severity")
    if severity is not None:
        try:
            severity = float(severity)
            scores["Eczema"] += severity * 0.60
            scores["Tinea Infection"] += severity * 0.20
            scores["Leishmaniasis"] -= severity * 0.10
        except (ValueError, TypeError):
            pass

    # RULE 6: Duration
    duration_val = symptoms_dict.get("duration_value")
    duration_unit = _normalize_value(symptoms_dict.get("duration_unit"))
    
    if duration_val is not None:
        try:
            val = float(duration_val)
            days = val
            if duration_unit == "weeks":
                days = val * 7.0
            elif duration_unit == "months":
                days = val * 30.0
                
            if days >= 90:
                scores["Eczema"] += 1.0
                scores["Leishmaniasis"] += 0.8
                scores["Tinea Infection"] += 0.4
            elif 30 <= days < 90:
                scores["Eczema"] += 0.6
                scores["Leishmaniasis"] += 0.4
                scores["Tinea Infection"] += 0.5
            elif days <= 14:
                scores["Tinea Infection"] += 0.4
                scores["Eczema"] += 0.3
        except (ValueError, TypeError):
            pass

    # RULE 7: Lesion Size
    size = symptoms_dict.get("lesion_size_cm")
    if size is not None:
        try:
            size_val = float(size)
            if size_val >= 10:
                scores["Leishmaniasis"] += 1.0
                scores["Eczema"] += 0.8
                scores["Tinea Infection"] += 0.5
            elif 5 <= size_val < 10:
                scores["Leishmaniasis"] += 0.6
                scores["Eczema"] += 0.4
                scores["Tinea Infection"] += 0.3
        except (ValueError, TypeError):
            pass

def _apply_tinea_incognito_rules(scores: Dict[str, float], symptoms_dict: Dict[str, Any]) -> None:
    """
    Apply special clinical rules, including Tinea Incognito.

    All comparisons use values produced by _normalize_value(), which lowercases
    AND converts underscores to spaces, matching what the HTML sends after
    normalisation (e.g. "topical_steroid" → "topical steroid").
    """
    shape = _normalize_value(symptoms_dict.get("lesion_shape"))       # "irregular", "circular", …
    treatment = _normalize_value(symptoms_dict.get("previous_treatment"))  # "topical steroid", "none", …
    border = _normalize_value(symptoms_dict.get("lesion_border"))     # "well defined raised", "ill defined", …
    scaling = bool(symptoms_dict.get("scaling"))
    ring_shaped = bool(symptoms_dict.get("ring_shaped"))
    central_clearing = bool(symptoms_dict.get("central_clearing"))

    # RULE 1 - Tinea Incognito
    # "topical_steroid" (HTML) → _normalize_value → "topical steroid"  ✅ FIXED
    if shape == "irregular" and treatment == "topical steroid":
        scores["Tinea Infection"] += 8.0
        scores["Eczema"] -= 3.0
        scores["Leishmaniasis"] -= 3.0
        if scaling:
            scores["Tinea Infection"] += 2.0

    # RULE 2 - Irregular without treatment
    if shape == "irregular" and treatment == "none":
        scores["Tinea Infection"] -= 6.0

    # RULE 3 - Irregular + Ill-defined without treatment
    # "ill_defined" (HTML) → _normalize_value → "ill defined"  ✅ FIXED (was "ill-defined diffuse")
    if shape == "irregular" and border in ["ill defined", "irregular"] and treatment == "none":
        scores["Tinea Infection"] -= 4.0

    # RULE 4 - Classic Synergy
    # "well_defined_raised" (HTML) → _normalize_value → "well defined raised"  ✅ FIXED
    if ring_shaped and central_clearing:
        scores["Tinea Infection"] += 5.0
        if border in ["well defined", "well defined raised"]:
            scores["Tinea Infection"] += 3.0

def _softmax(scores: Dict[str, float], temperature: float = 4.0) -> Dict[str, float]:
    """Convert raw scores to probabilities using softmax with temperature."""
    max_score = max(scores.values()) if scores else 0
    
    exps = {condition: math.exp((score - max_score) / temperature) 
            for condition, score in scores.items()}
            
    sum_exps = sum(exps.values())
    
    if sum_exps == 0:
        return {condition: 0.0 for condition in scores}
        
    return {condition: exp_val / sum_exps for condition, exp_val in exps.items()}

def _convert_to_percentages(probs: Dict[str, float]) -> Dict[str, int]:
    """Convert probabilities to rounded percentages."""
    return {condition: round(prob * 100) for condition, prob in probs.items()}

def _apply_central_clearing_cap(percentages: Dict[str, int], symptoms_dict: Dict[str, Any]) -> None:
    """Apply Rule 8: Central Clearing Cap."""
    central_clearing = bool(symptoms_dict.get("central_clearing"))
    
    if not central_clearing and percentages.get("Tinea Infection", 0) > 95:
        excess = percentages["Tinea Infection"] - 95
        percentages["Tinea Infection"] = 95
        
        others = [k for k in percentages.keys() if k != "Tinea Infection"]
        if others:
            highest_other = max(others, key=lambda k: percentages[k])
            percentages[highest_other] += excess

def analyse_symptoms(symptoms: Any) -> Dict[str, Any]:
    """
    Analyze symptoms and return ranked conditions with percentages and debug info.
    
    Args:
        symptoms: SQLAlchemy model, Pydantic model, or Dictionary of symptom inputs.
        
    Returns:
        Dictionary containing analysis type, ranked conditions, raw scores,
        selected features, and debug payload.
    """
    symptoms_dict = _to_dict(symptoms)
    logger.debug(f"Starting symptom analysis with parsed input: {symptoms_dict}")
    
    scores = {condition: 0.0 for condition in DISEASE_WEIGHTS}
    active_features = _selected_features(symptoms_dict)
    
    # Apply base weights
    for condition, weights in DISEASE_WEIGHTS.items():
        for feature in active_features:
            if feature in weights:
                scores[condition] += weights[feature]
                
    # Apply numeric scoring rules
    _apply_numeric_scores(scores, symptoms_dict)
    
    # Apply special clinical rules
    _apply_tinea_incognito_rules(scores, symptoms_dict)
    
    # Convert to probabilities via Softmax
    probs = _softmax(scores, temperature=4.0)
    
    # Convert to percentages
    percentages = _convert_to_percentages(probs)
    
    # Apply Rule 8: Central Clearing Cap
    _apply_central_clearing_cap(percentages, symptoms_dict)
    
    # Sort conditions by percentage
    ranked_conditions = [
        {"condition": k, "percentage": v} 
        for k, v in sorted(percentages.items(), key=lambda item: item[1], reverse=True)
    ]
    
    result = {
        "analysis_type": "weighted_symptom_decision_support_v2",
        "ranked_conditions": ranked_conditions,
        "raw_scores": {k: round(v, 2) for k, v in scores.items()},
        "selected_features": active_features,
        "debug": {
            "symptoms_found": symptoms_dict
        }
    }
    
    logger.debug(f"Analysis complete. Ranked conditions: {ranked_conditions}")
    return result