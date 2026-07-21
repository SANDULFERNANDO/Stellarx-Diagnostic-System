from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.database import get_db
from app.models import PatientCase
from app.schemas import CaseCreate, CaseResponse, CaseUpdate
from app.auth_utils import get_current_user
from app.models import HealthcareWorker

router = APIRouter(prefix="/cases", tags=["Cases"])

@router.post("/", response_model=CaseResponse)
def create_case(
    case: CaseCreate,
    db: Session = Depends(get_db),
    current_user: HealthcareWorker = Depends(get_current_user)
):
    year = date.today().year
    count = db.query(PatientCase).filter(PatientCase.case_id.like(f"TZN-{year}-%")).count()
    case_id = f"TZN-{year}-{count+1:04d}"
    new_case = PatientCase(
        case_id=case_id,
        worker_id=current_user.user_id,
        case_date=date.today(),
        patient_age=case.patient_age,
        patient_gender=case.patient_gender,
        patient_location=case.patient_location,
        status="DRAFT"
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return new_case

@router.get("/", response_model=List[CaseResponse])
def list_cases(db: Session = Depends(get_db), current_user: HealthcareWorker = Depends(get_current_user)):
    return db.query(PatientCase).filter(PatientCase.worker_id == current_user.user_id).order_by(PatientCase.created_at.desc()).all()

@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: str, db: Session = Depends(get_db), current_user: HealthcareWorker = Depends(get_current_user)):
    case = db.query(PatientCase).filter(PatientCase.case_id == case_id, PatientCase.worker_id == current_user.user_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.put("/{case_id}", response_model=CaseResponse)
def update_case(case_id: str, case_update: CaseUpdate, db: Session = Depends(get_db), current_user: HealthcareWorker = Depends(get_current_user)):
    case = db.query(PatientCase).filter(PatientCase.case_id == case_id, PatientCase.worker_id == current_user.user_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if case_update.patient_age is not None:
        case.patient_age = case_update.patient_age
    if case_update.patient_gender is not None:
        case.patient_gender = case_update.patient_gender
    if case_update.patient_location is not None:
        case.patient_location = case_update.patient_location
    db.commit()
    db.refresh(case)
    return case

@router.delete("/{case_id}")
def delete_case(case_id: str, db: Session = Depends(get_db), current_user: HealthcareWorker = Depends(get_current_user)):
    case = db.query(PatientCase).filter(PatientCase.case_id == case_id, PatientCase.worker_id == current_user.user_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    db.delete(case)
    db.commit()
    return {"message": "Case deleted"}