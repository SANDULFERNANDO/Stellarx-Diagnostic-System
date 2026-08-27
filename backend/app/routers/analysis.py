import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth_utils import get_current_user
from app.database import get_db
from app.models import HealthcareWorker, PatientCase, Symptom
from app.services.symptom_scoring import analyse_symptoms

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
    # Step 3: Execute the symptom scoring model
    # ------------------------------------------------------------------
    try:
        result = analyse_symptoms(symptom)
        logger.info(
            f"Symptom analysis completed for case {case_id}. "
            f"Top condition: {result['ranked_conditions'][0]['condition']} "
            f"({result['ranked_conditions'][0]['percentage']}%)"
        )

    except Exception as e:
        logger.error(
            f"Symptom analysis failed for case {case_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Analysis failed",
                "message": "The symptom scoring model encountered an internal error.",
                "case_id": case_id,
                "technical_details": str(e) if logger.isEnabledFor(logging.DEBUG) else None,
            },
        )

    # ------------------------------------------------------------------
    # Step 4: Return structured response
    # ------------------------------------------------------------------
    response = {
        "case_id": case_id,
        "analysis_type": result.get("analysis_type", "weighted_symptom_decision_support"),
        "ranked_conditions": result.get("ranked_conditions", []),
        "raw_scores": result.get("raw_scores", {}),
        "selected_features": result.get("selected_features", []),
        "metadata": {
            "model_version": "v2.0",
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
    description="Retrieve the last symptom analysis result for a case.",
)
def get_analysis_result(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: HealthcareWorker = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Fetch the most recent symptom analysis result for a case.

    Currently, this re-runs the analysis. In the future, you can store
    results in an `analysis_results` table and query that instead.
    """
    return run_symptom_analysis(case_id, db, current_user)