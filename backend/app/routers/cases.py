# backend/app/routers/cases.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from ..database import get_db
from ..models import PatientCase
from ..schemas import CaseCreate, CaseResponse
from ..auth_utils import get_current_user

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.post("/", response_model=CaseResponse)
def create_case(
    case: CaseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new patient case"""
    # Generate case ID: TZN-YYYY-XXXX
    year = date.today().year
    count = db.query(PatientCase).filter(
        PatientCase.case_id.like(f"TZN-{year}-%")
    ).count()
    case_id = f"TZN-{year}-{count+1:04d}"
    
    # Create new case
    new_case = PatientCase(
        case_id=case_id,
        worker_id=current_user['user_id'],
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
def list_cases(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all cases for the current user"""
    cases = db.query(PatientCase).filter(
        PatientCase.worker_id == current_user['user_id']
    ).order_by(PatientCase.created_at.desc()).all()
    return cases


@router.get("/{case_id}", response_model=CaseResponse)
def get_case(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific case by ID"""
    case = db.query(PatientCase).filter(
        PatientCase.case_id == case_id,
        PatientCase.worker_id == current_user['user_id']
    ).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    return case


@router.put("/{case_id}", response_model=CaseResponse)
def update_case(
    case_id: str,
    case_update: CaseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a case"""
    case = db.query(PatientCase).filter(
        PatientCase.case_id == case_id,
        PatientCase.worker_id == current_user['user_id']
    ).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    case.patient_age = case_update.patient_age
    case.patient_gender = case_update.patient_gender
    case.patient_location = case_update.patient_location
    
    db.commit()
    db.refresh(case)
    return case


@router.delete("/{case_id}")
def delete_case(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a case"""
    case = db.query(PatientCase).filter(
        PatientCase.case_id == case_id,
        PatientCase.worker_id == current_user['user_id']
    ).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    db.delete(case)
    db.commit()
    return {"message": "Case deleted successfully"}