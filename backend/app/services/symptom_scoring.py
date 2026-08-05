import math
from typing import Any, Dict, List


TARGET_CLASSES = [
    "Tinea Infection",
    "Psoriasis",
    "Eczema",
]


# ============================================================
# BASE SYMPTOM WEIGHTS
# ============================================================

DISEASE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "Tinea Infection": {
        # Visual appearance
        "redness": 2.0,
        "scaling": 3.0,
        "ring_shaped": 6.0,
        "itching": 2.5,

        # Other clinical signs
        "pain": -0.5,
        "central_clearing": 1.0,
        "nail_changes": 0.0,

        # Lesion border
        "border_well_defined_raised": 4.0,
        "border_well_defined": 3.0,
        "border_ill_defined": -1.5,
        "border_irregular": -0.5,

        # Lesion shape
        "shape_circular": 5.0,
        "shape_irregular": 0.0,
        "shape_multiple": 0.5,

        # Lesion colour
        "color_red": 1.0,
        "color_pink": 0.5,
        "color_brown": 0.3,
        "color_silver_white": 0.2,
        "color_dark": 0.2,

        # Locations
        "location_arms": 0.8,
        "location_legs": 0.8,
        "location_face": 0.4,
        "location_hands": 0.4,
        "location_feet": 0.8,
        "location_scalp": 0.4,
        "location_back": 0.4,
        "location_neck": 0.4,
        "location_chest": 0.4,
        "location_abdomen": 0.4,

        # Previous treatment
        "treatment_topical_steroid": 0.5,
        "treatment_antifungal_cream": 1.0,
        "treatment_oral_antifungal": 1.0,
    },

    "Psoriasis": {
        "redness": 2.5,
        "scaling": 4.5,
        "ring_shaped": -1.5,
        "itching": 1.5,
        "pain": 1.0,
        "central_clearing": -2.0,
        "nail_changes": 3.5,

        "border_well_defined": 2.0,
        "border_well_defined_raised": 1.5,
        "border_irregular": 0.5,
        "border_ill_defined": -0.5,

        "shape_circular": 0.5,
        "shape_irregular": 1.0,
        "shape_multiple": 2.0,

        "color_red": 1.5,
        "color_pink": 1.0,
        "color_brown": 0.4,
        "color_silver_white": 4.5,
        "color_dark": 0.5,

        "location_arms": 1.0,
        "location_legs": 1.0,
        "location_face": 0.2,
        "location_hands": 1.0,
        "location_feet": 1.0,
        "location_scalp": 3.0,
        "location_back": 1.0,
        "location_neck": 0.5,
        "location_chest": 0.5,
        "location_abdomen": 0.5,

        "treatment_topical_steroid": 1.0,
        "treatment_antifungal_cream": -0.5,
        "treatment_oral_antifungal": -0.5,
    },

    "Eczema": {
        "redness": 3.0,
        "scaling": 2.0,
        "ring_shaped": -2.0,
        "itching": 4.5,
        "pain": 1.0,
        "central_clearing": -2.0,
        "nail_changes": 0.0,

        "border_well_defined": -0.5,
        "border_well_defined_raised": -1.0,
        "border_irregular": 2.0,
        "border_ill_defined": 3.0,

        "shape_circular": -0.5,
        "shape_irregular": 2.5,
        "shape_multiple": 1.0,

        "color_red": 2.0,
        "color_pink": 1.5,
        "color_brown": 0.8,
        "color_silver_white": 0.5,
        "color_dark": 0.8,

        "location_arms": 1.5,
        "location_legs": 1.5,
        "location_face": 1.0,
        "location_hands": 2.0,
        "location_feet": 1.0,
        "location_scalp": 0.5,
        "location_back": 0.5,
        "location_neck": 1.5,
        "location_chest": 0.5,
        "location_abdomen": 0.5,

        "treatment_topical_steroid": 1.5,
        "treatment_antifungal_cream": -0.5,
        "treatment_oral_antifungal": -0.5,
    },
}


# ============================================================
# NORMALIZATION
# ============================================================

def _normalize_value(value: Any) -> str:
    return (
        str(value or "")
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
        .replace(",", "")
    )


# ============================================================
# FEATURE EXTRACTION
# ============================================================

def _selected_features(symptoms: Any) -> List[str]:
    features: List[str] = []

    boolean_fields = [
        "redness",
        "scaling",
        "ring_shaped",
        "itching",
        "pain",
        "central_clearing",
        "nail_changes",
    ]

    for field in boolean_fields:
        if bool(getattr(symptoms, field, False)):
            features.append(field)

    # Lesion border
    border = _normalize_value(
        getattr(symptoms, "lesion_border", None)
    )

    border_aliases = {
        "well_defined": "border_well_defined",
        "well_defined_raised": "border_well_defined_raised",
        "ill_defined": "border_ill_defined",
        "irregular": "border_irregular",
    }

    if border in border_aliases:
        features.append(border_aliases[border])

    # Lesion shape
    shape = _normalize_value(
        getattr(symptoms, "lesion_shape", None)
    )

    shape_aliases = {
        "circular": "shape_circular",
        "irregular": "shape_irregular",
        "multiple": "shape_multiple",
        "multiple_lesions": "shape_multiple",
    }

    if shape in shape_aliases:
        features.append(shape_aliases[shape])

    # Lesion colour
    color = _normalize_value(
        getattr(symptoms, "lesion_color", None)
    )

    color_aliases = {
        "red": "color_red",
        "pink": "color_pink",
        "brown": "color_brown",
        "silver_white": "color_silver_white",
        "silvery_white": "color_silver_white",
        "dark": "color_dark",
    }

    if color in color_aliases:
        features.append(color_aliases[color])

    # Lesion locations
    locations = getattr(
        symptoms,
        "lesion_locations",
        [],
    ) or []

    if isinstance(locations, str):
        locations = [
            location.strip()
            for location in locations.split(",")
            if location.strip()
        ]

    for location in locations:
        normalized_location = _normalize_value(location)

        if normalized_location:
            features.append(
                f"location_{normalized_location}"
            )

    # Previous treatment
    treatment = _normalize_value(
        getattr(symptoms, "previous_treatment", None)
    )

    treatment_aliases = {
        "antifungal_cream": "treatment_antifungal_cream",
        "oral_antifungal": "treatment_oral_antifungal",
        "topical_steroid": "treatment_topical_steroid",
    }

    if treatment in treatment_aliases:
        features.append(treatment_aliases[treatment])

    return features


# ============================================================
# NUMERIC INPUT SCORING
# ============================================================

def _apply_numeric_scores(
    symptoms: Any,
    raw_scores: Dict[str, float],
) -> None:
    itch_severity = getattr(
        symptoms,
        "itch_severity",
        None,
    )

    lesion_size = getattr(
        symptoms,
        "lesion_size_cm",
        None,
    )

    duration_value = getattr(
        symptoms,
        "duration_value",
        None,
    )

    duration_unit = _normalize_value(
        getattr(symptoms, "duration_unit", None)
    )

    # Itch severity
    if itch_severity is not None:
        itch = float(itch_severity)

        raw_scores["Eczema"] += itch * 0.45
        raw_scores["Tinea Infection"] += itch * 0.20
        raw_scores["Psoriasis"] += itch * 0.12

    # Lesion size
    if lesion_size is not None:
        size = float(lesion_size)

        if size >= 10:
            raw_scores["Psoriasis"] += 1.0
            raw_scores["Eczema"] += 0.8
            raw_scores["Tinea Infection"] += 0.5

        elif size >= 5:
            raw_scores["Psoriasis"] += 0.5
            raw_scores["Eczema"] += 0.4
            raw_scores["Tinea Infection"] += 0.3

    # Duration
    if duration_value is not None:
        duration = float(duration_value)

        days_multiplier = {
            "days": 1,
            "weeks": 7,
            "months": 30,
        }.get(duration_unit, 1)

        duration_days = duration * days_multiplier

        if duration_days >= 90:
            raw_scores["Psoriasis"] += 1.5
            raw_scores["Eczema"] += 1.0
            raw_scores["Tinea Infection"] += 0.4

        elif duration_days >= 30:
            raw_scores["Psoriasis"] += 0.8
            raw_scores["Eczema"] += 0.6
            raw_scores["Tinea Infection"] += 0.5

        elif duration_days <= 14:
            raw_scores["Tinea Infection"] += 0.4
            raw_scores["Eczema"] += 0.3


# ============================================================
# SPECIAL TINEA LOGIC
# ============================================================

def _apply_tinea_logic(
    symptoms: Any,
    raw_scores: Dict[str, float],
) -> None:
    """
    Project-specific Tinea compatibility rules.

    Tinea score increases when:
    - Redness is selected.
    - Scaling is selected.
    - Ring-shaped lesion is selected.
    - Itching is selected.
    - Border is well-defined or well-defined raised.
    - Shape is circular.
    - Shape is irregular only when previous treatment was given.

    Tinea score decreases when:
    - Shape is irregular and previous treatment is none.
    """

    redness = bool(
        getattr(symptoms, "redness", False)
    )

    scaling = bool(
        getattr(symptoms, "scaling", False)
    )

    ring_shaped = bool(
        getattr(symptoms, "ring_shaped", False)
    )

    itching = bool(
        getattr(symptoms, "itching", False)
    )

    border = _normalize_value(
        getattr(symptoms, "lesion_border", None)
    )

    shape = _normalize_value(
        getattr(symptoms, "lesion_shape", None)
    )

    previous_treatment = _normalize_value(
        getattr(symptoms, "previous_treatment", None)
    )

    treatments_given = {
        "topical_steroid",
        "antifungal_cream",
        "oral_antifungal",
    }

    treatment_was_given = (
        previous_treatment in treatments_given
    )

    # --------------------------------------------------------
    # Rule 1: Visual appearance combination
    # --------------------------------------------------------

    visual_symptom_count = sum([
        redness,
        scaling,
        ring_shaped,
        itching,
    ])

    if visual_symptom_count == 4:
        # All four main Tinea features selected
        raw_scores["Tinea Infection"] += 10.0

    elif visual_symptom_count == 3:
        raw_scores["Tinea Infection"] += 5.0

    elif visual_symptom_count == 2:
        raw_scores["Tinea Infection"] += 2.0

    elif visual_symptom_count == 1:
        raw_scores["Tinea Infection"] += 0.5

    # Ring-shaped lesion is a strong Tinea feature
    if ring_shaped:
        raw_scores["Tinea Infection"] += 3.0

    # Scaling plus ring shape combination
    if scaling and ring_shaped:
        raw_scores["Tinea Infection"] += 3.0

    # Itching plus ring shape combination
    if itching and ring_shaped:
        raw_scores["Tinea Infection"] += 2.0

    # --------------------------------------------------------
    # Rule 2: Lesion border
    # --------------------------------------------------------

    if border == "well_defined_raised":
        raw_scores["Tinea Infection"] += 5.0

    elif border == "well_defined":
        raw_scores["Tinea Infection"] += 4.0

    elif border == "ill_defined":
        raw_scores["Tinea Infection"] -= 2.0

    # --------------------------------------------------------
    # Rule 3: Circular lesion shape
    # --------------------------------------------------------

    if shape == "circular":
        raw_scores["Tinea Infection"] += 6.0

    # Circular + ring-shaped combination
    if shape == "circular" and ring_shaped:
        raw_scores["Tinea Infection"] += 4.0

    # Circular + well-defined border combination
    if (
        shape == "circular"
        and border in {
            "well_defined",
            "well_defined_raised",
        }
    ):
        raw_scores["Tinea Infection"] += 3.0

    # --------------------------------------------------------
    # Rule 4:
    # Irregular shape is accepted when treatment was given
    # --------------------------------------------------------

    if shape == "irregular" and treatment_was_given:
        raw_scores["Tinea Infection"] += 4.5

        # Treatment may alter the normal appearance
        if ring_shaped or scaling:
            raw_scores["Tinea Infection"] += 2.0

    # --------------------------------------------------------
    # Rule 5:
    # Irregular shape with no previous treatment
    # should not strongly support Tinea
    # --------------------------------------------------------

    if (
        shape == "irregular"
        and previous_treatment == "none"
    ):
        raw_scores["Tinea Infection"] -= 8.0

    # Unknown treatment is not considered confirmed treatment
    if (
        shape == "irregular"
        and previous_treatment == "unknown"
    ):
        raw_scores["Tinea Infection"] -= 3.0

    # --------------------------------------------------------
    # Additional consistency penalties
    # --------------------------------------------------------

    if shape == "irregular" and not ring_shaped:
        raw_scores["Tinea Infection"] -= 2.0

    if (
        border == "ill_defined"
        and shape == "irregular"
        and not treatment_was_given
    ):
        raw_scores["Tinea Infection"] -= 3.0


# ============================================================
# SOFTMAX PROBABILITY CONVERSION
# ============================================================

def _softmax(
    raw_scores: Dict[str, float],
    temperature: float = 4.0,
) -> Dict[str, float]:
    highest_score = max(raw_scores.values())

    exponential_scores = {
        condition: math.exp(
            (score - highest_score) / temperature
        )
        for condition, score in raw_scores.items()
    }

    total = sum(exponential_scores.values())

    if total <= 0:
        equal_probability = 1 / len(raw_scores)

        return {
            condition: equal_probability
            for condition in raw_scores
        }

    return {
        condition: value / total
        for condition, value in exponential_scores.items()
    }


# ============================================================
# PERCENTAGE CONVERSION
# ============================================================

def _convert_to_percentages(
    probabilities: Dict[str, float]
) -> List[Dict[str, Any]]:
    ranked = sorted(
        [
            {
                "condition": condition,
                "percentage": round(
                    probability * 100
                ),
            }
            for condition, probability
            in probabilities.items()
        ],
        key=lambda item: item["percentage"],
        reverse=True,
    )

    percentage_total = sum(
        item["percentage"]
        for item in ranked
    )

    # Ensure total equals exactly 100
    if ranked and percentage_total != 100:
        ranked[0]["percentage"] += (
            100 - percentage_total
        )

    return ranked


# ============================================================
# FINAL CENTRAL-CLEARING RULE
# ============================================================

def _apply_final_tinea_percentage_rule(
    symptoms: Any,
    ranked_conditions: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Final rule:
    - Central Clearing = Yes:
      Tinea may naturally reach 100% if the other rules are also strong.
    - Central Clearing = No:
      Tinea is capped at 95%, so it can never display 100%.
    """

    central_clearing = bool(
        getattr(symptoms, "central_clearing", False)
    )

    tinea_item = next(
        (
            item
            for item in ranked_conditions
            if item["condition"] == "Tinea Infection"
        ),
        None,
    )

    if tinea_item is None:
        return ranked_conditions

    if (
        not central_clearing
        and tinea_item["percentage"] > 95
    ):
        removed_percentage = (
            tinea_item["percentage"] - 95
        )

        tinea_item["percentage"] = 95

        other_conditions = [
            item
            for item in ranked_conditions
            if item["condition"] != "Tinea Infection"
        ]

        if other_conditions:
            strongest_other = max(
                other_conditions,
                key=lambda item: item["percentage"],
            )

            strongest_other["percentage"] += (
                removed_percentage
            )

    ranked_conditions.sort(
        key=lambda item: item["percentage"],
        reverse=True,
    )

    return ranked_conditions


# ============================================================
# MAIN ANALYSIS FUNCTION
# ============================================================

def analyse_symptoms(
    symptoms: Any
) -> Dict[str, Any]:
    selected_features = _selected_features(
        symptoms
    )

    raw_scores: Dict[str, float] = {
        condition: 0.0
        for condition in TARGET_CLASSES
    }

    # Apply base weights
    for condition in TARGET_CLASSES:
        condition_weights = DISEASE_WEIGHTS[
            condition
        ]

        for feature in selected_features:
            raw_scores[condition] += (
                condition_weights.get(
                    feature,
                    0.0,
                )
            )

    # Apply numeric input scoring
    _apply_numeric_scores(
        symptoms,
        raw_scores,
    )

    # Apply special Tinea logic
    _apply_tinea_logic(
        symptoms,
        raw_scores,
    )

    # Convert scores to probabilities
    probabilities = _softmax(
        raw_scores,
        temperature=4.0,
    )

    # Convert probabilities to percentages
    ranked_conditions = (
        _convert_to_percentages(
            probabilities
        )
    )

    # Central Clearing = No means Tinea cannot display 100%.
    ranked_conditions = (
        _apply_final_tinea_percentage_rule(
            symptoms,
            ranked_conditions,
        )
    )

    return {
        "analysis_type": (
            "weighted_symptom_decision_support"
        ),

        "ranked_conditions": (
            ranked_conditions
        ),

        # Useful during development and testing
        "raw_scores": {
            condition: round(score, 2)
            for condition, score
            in raw_scores.items()
        },

        "selected_features": (
            selected_features
        ),
    }