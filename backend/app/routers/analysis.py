import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth_utils import get_current_user
from app.database import get_db
from app.models import HealthcareWorker, PatientCase, Symptom, AnalysisResult, Image
from app.services.symptom_scoring import analyse_symptoms
from app.services.hybrid_scoring import get_real_image_prediction, fuse_predictions
import json

# Configure module logger
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/cases/{case_id}/analysis",
    tags=["Analysis"],
)


@router.post(
    "/",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Run Symptom-Based Analysis",
    description="""
    Executes the weighted symptom scoring model for a given case.
    
    The model uses dermatologist-derived clinical weights to analyse:
    - Visual appearance (redness, scaling, ring-shaped)
    - Sensation (itching, pain)
    - Lesion characteristics (border, shape, colour, size)
    - Location, duration, and previous treatment
    - Special clinical patterns (Tinea incognito, synergy rules)
    
    Returns a ranked list of conditions with percentage probabilities.
    """,
)
def run_symptom_analysis(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: HealthcareWorker = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Execute the symptom-based diagnostic model for a specific case.

    Steps:
    1. Validate case exists and belongs to the current user.
    2. Retrieve symptom data for the case.
    3. Run the weighted scoring model.
    4. Return structured results including ranked conditions, raw scores,
       and selected features.

    Raises:
        HTTPException 404: Case not found or symptoms not recorded.
    """
    logger.info(
        f"Symptom analysis requested for case: {case_id} by user: {current_user.user_id}"
    )

    # ------------------------------------------------------------------
    # Step 1: Fetch and validate the patient case
    # ------------------------------------------------------------------
    patient_case = (
        db.query(PatientCase)
        .filter(
            PatientCase.case_id == case_id,
            PatientCase.worker_id == current_user.user_id,
        )
        .first()
    )

    if not patient_case:
        logger.warning(
            f"Case {case_id} not found or not owned by user {current_user.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Case not found",
                "message": f"No case found with ID: {case_id}",
                "case_id": case_id,
            },
        )

    logger.debug(f"Case found: {patient_case.case_id} (UUID: {patient_case.id})")

    # ------------------------------------------------------------------
    # Step 2: Fetch symptom data linked to the case
    # ------------------------------------------------------------------
    # ✅ CORRECTED: Your symptoms.case_id stores the UUID, not the TZN string.
    # So we MUST use patient_case.id (the UUID).
    # ------------------------------------------------------------------
    symptom = (
        db.query(Symptom)
        .filter(Symptom.case_id == patient_case.id)  # <-- ✅ FIXED: Uses UUID
        .first()
    )

    if not symptom:
        logger.warning(
            f"Symptoms not found for case {case_id} (patient_case.id: {patient_case.id})"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Symptoms not recorded",
                "message": (
                    f"Please complete and submit the symptom form for case {case_id} "
                    "before running the analysis."
                ),
                "case_id": case_id,
                "symptom_status": "missing",
            },
        )

    logger.debug(
        f"Symptoms found for case {case_id}: "
        f"redness={symptom.redness}, scaling={symptom.scaling}, "
        f"ring_shaped={symptom.ring_shaped}, itching={symptom.itching}"
    )

    # ------------------------------------------------------------------
    # Step 3: Execute the hybrid scoring model
    # ------------------------------------------------------------------
    try:
        # 3a. Run Symptom Model
        symptom_result = analyse_symptoms(symptom)
        
        # Convert symptom ranked_conditions to a probability dict
        symptom_probs = {
            item["condition"]: item["percentage"] 
            for item in symptom_result.get("ranked_conditions", [])
        }
        
        # Fetch image S3 keys for the case
        images = db.query(Image).filter(Image.case_id == patient_case.id).all()
        s3_keys = [img.s3_key for img in images]
        
        # 3b. Run Real Image Model
        image_probs = get_real_image_prediction(s3_keys)
        
        # 3c. Fuse Predictions
        fusion_result = fuse_predictions(symptom_probs, image_probs)
        
        final_probs = fusion_result["final_probabilities"]
        
        # 3d. Create Ranked Conditions for the Frontend (using Fused Probs)
        ranked_conditions = [
            {"condition": k, "percentage": v}
            for k, v in sorted(final_probs.items(), key=lambda item: item[1], reverse=True)
        ]
        
        logger.info(
            f"Hybrid analysis completed for case {case_id}. "
            f"Top condition: {fusion_result['final_diagnosis']} "
            f"({fusion_result['final_confidence']}%)"
        )
        
        # 3e. Save to Database
        # Check if one already exists
        existing_result = db.query(AnalysisResult).filter(AnalysisResult.case_id == patient_case.id).first()
        
        if existing_result:
            existing_result.symptom_diagnosis = symptom_result['ranked_conditions'][0]['condition']
            existing_result.symptom_confidence = symptom_result['ranked_conditions'][0]['percentage']
            existing_result.symptom_probabilities = json.dumps(symptom_probs)
            existing_result.image_diagnosis = max(image_probs.items(), key=lambda x: x[1])[0]
            existing_result.image_confidence = max(image_probs.items(), key=lambda x: x[1])[1]
            existing_result.image_probabilities = json.dumps(image_probs)
            existing_result.final_diagnosis = fusion_result["final_diagnosis"]
            existing_result.final_confidence = fusion_result["final_confidence"]
            existing_result.final_probabilities = json.dumps(final_probs)
        else:
            new_result = AnalysisResult(
                case_id=patient_case.id,
                symptom_diagnosis=symptom_result['ranked_conditions'][0]['condition'],
                symptom_confidence=symptom_result['ranked_conditions'][0]['percentage'],
                symptom_probabilities=json.dumps(symptom_probs),
                image_diagnosis=max(image_probs.items(), key=lambda x: x[1])[0],
                image_confidence=max(image_probs.items(), key=lambda x: x[1])[1],
                image_probabilities=json.dumps(image_probs),
                final_diagnosis=fusion_result["final_diagnosis"],
                final_confidence=fusion_result["final_confidence"],
                final_probabilities=json.dumps(final_probs)
            )
            db.add(new_result)
        
        db.commit()

    except Exception as e:
        logger.error(
            f"Analysis failed for case {case_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Analysis failed",
                "message": "The hybrid scoring model encountered an internal error.",
                "case_id": case_id,
                "technical_details": str(e) if logger.isEnabledFor(logging.DEBUG) else None,
            },
        )

    # ------------------------------------------------------------------
    # Step 4: Return structured response
    # ------------------------------------------------------------------
    response = {
        "case_id": case_id,
        "analysis_type": "hybrid_symptom_image_fusion",
        "ranked_conditions": ranked_conditions,
        "raw_scores": symptom_result.get("raw_scores", {}),
        "selected_features": symptom_result.get("selected_features", []),
        "hybrid_details": {
            "symptom_probabilities": symptom_probs,
            "image_probabilities": image_probs,
            "final_probabilities": final_probs,
            "final_diagnosis": fusion_result["final_diagnosis"]
        },
        "metadata": {
            "model_version": "v3.0-hybrid-beta",
        },
        "disclaimer": (
            "This is an AI-assisted decision support tool based on weighted clinical criteria. "
            "It is not a definitive diagnosis and must be interpreted by a qualified "
            "healthcare professional in conjunction with clinical examination and, "
            "where appropriate, laboratory investigations."
        ),
    }

    logger.debug(f"Response prepared for case {case_id}")
    return response


# ------------------------------------------------------------------
# Optional: GET endpoint to retrieve previous analysis results
# ------------------------------------------------------------------
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Get Analysis Results",
    description="Retrieve the last analysis result for a case from the database.",
)
def get_analysis_result(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: HealthcareWorker = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Fetch the most recent hybrid analysis result for a case.
    """
    patient_case = (
        db.query(PatientCase)
        .filter(
            PatientCase.case_id == case_id,
            PatientCase.worker_id == current_user.user_id,
        )
        .first()
    )

    if not patient_case:
        raise HTTPException(status_code=404, detail="Case not found")

    result = db.query(AnalysisResult).filter(AnalysisResult.case_id == patient_case.id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Analysis result not found")

    # Reconstruct the expected frontend JSON format from the DB record
    final_probs = json.loads(result.final_probabilities)
    ranked_conditions = [
        {"condition": k, "percentage": v}
        for k, v in sorted(final_probs.items(), key=lambda item: item[1], reverse=True)
    ]
    
    return {
        "case_id": case_id,
        "analysis_type": "hybrid_symptom_image_fusion",
        "ranked_conditions": ranked_conditions,
        "hybrid_details": {
            "symptom_probabilities": json.loads(result.symptom_probabilities),
            "image_probabilities": json.loads(result.image_probabilities) if result.image_probabilities else None,
            "final_probabilities": final_probs,
            "final_diagnosis": result.final_diagnosis
        }
    }