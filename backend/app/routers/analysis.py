from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth_utils import get_current_user
from app.database import get_db
from app.models import HealthcareWorker, PatientCase, Symptom
from app.services.symptom_scoring import analyse_symptoms


router = APIRouter(
    prefix="/cases/{case_id}/analysis",
    tags=["Analysis"],
)


@router.post("/")
def run_symptom_analysis(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: HealthcareWorker = Depends(get_current_user),
):
    patient_case = (
        db.query(PatientCase)
        .filter(
            PatientCase.case_id == case_id,
            PatientCase.worker_id == current_user.user_id,
        )
        .first()
    )

    if not patient_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )

    symptom = (
        db.query(Symptom)
        .filter(Symptom.case_id == patient_case.id)
        .first()
    )

    if not symptom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Symptoms have not been saved for this case",
        )

    return analyse_symptoms(symptom)