from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json

from app.database import get_db
from app.models import PatientCase, Symptom, HealthcareWorker
from app.auth_utils import get_current_user
from app.schemas import SymptomCreate, SymptomResponse

router = APIRouter(prefix="/cases/{case_id}/symptoms", tags=["Symptoms"])


@router.post("/", response_model=SymptomResponse)
async def create_symptoms(
    case_id: str,
    symptom_data: SymptomCreate,
    db: Session = Depends(get_db),
    current_user: HealthcareWorker = Depends(get_current_user)
):
    """
    Create or update symptoms for a case.
    """
    
    # 1. Validate case exists and belongs to user
    case = db.query(PatientCase).filter(
        PatientCase.case_id == case_id,
        PatientCase.worker_id == current_user.user_id
    ).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # 2. Check if symptoms already exist for this case
    existing_symptom = db.query(Symptom).filter(
        Symptom.case_id == case.id
    ).first()
    
    if existing_symptom:
        # Update existing symptoms
        existing_symptom.redness = symptom_data.redness
        existing_symptom.scaling = symptom_data.scaling
        existing_symptom.ring_shaped = symptom_data.ring_shaped
        existing_symptom.itching = symptom_data.itching
        existing_symptom.pain = symptom_data.pain
        
        existing_symptom.duration_value = symptom_data.duration_value
        existing_symptom.duration_unit = symptom_data.duration_unit
        existing_symptom.itch_severity = symptom_data.itch_severity
        
        existing_symptom.lesion_size_cm = symptom_data.lesion_size_cm
        existing_symptom.lesion_border = symptom_data.lesion_border
        existing_symptom.lesion_shape = symptom_data.lesion_shape
        existing_symptom.lesion_color = symptom_data.lesion_color
        existing_symptom.lesion_locations = json.dumps(symptom_data.lesion_locations) if symptom_data.lesion_locations else None
        
        existing_symptom.central_clearing = symptom_data.central_clearing
        existing_symptom.previous_treatment = symptom_data.previous_treatment
        existing_symptom.nail_changes = symptom_data.nail_changes
        
        existing_symptom.notes = symptom_data.notes
        
        db.commit()
        db.refresh(existing_symptom)
        
        # Convert locations back to list for response
        response_data = existing_symptom.__dict__.copy()
        if response_data.get('lesion_locations'):
            response_data['lesion_locations'] = json.loads(response_data['lesion_locations'])
        else:
            response_data['lesion_locations'] = []
        
        return response_data
    
    # 3. Create new symptoms
    new_symptom = Symptom(
        case_id=case.id,
        redness=symptom_data.redness,
        scaling=symptom_data.scaling,
        ring_shaped=symptom_data.ring_shaped,
        itching=symptom_data.itching,
        pain=symptom_data.pain,
        duration_value=symptom_data.duration_value,
        duration_unit=symptom_data.duration_unit,
        itch_severity=symptom_data.itch_severity,
        lesion_size_cm=symptom_data.lesion_size_cm,
        lesion_border=symptom_data.lesion_border,
        lesion_shape=symptom_data.lesion_shape,
        lesion_color=symptom_data.lesion_color,
        lesion_locations=json.dumps(symptom_data.lesion_locations) if symptom_data.lesion_locations else None,
        central_clearing=symptom_data.central_clearing,
        previous_treatment=symptom_data.previous_treatment,
        nail_changes=symptom_data.nail_changes,
        notes=symptom_data.notes
    )
    
    db.add(new_symptom)
    db.commit()
    db.refresh(new_symptom)
    
    # Convert locations back to list for response
    response_data = new_symptom.__dict__.copy()
    if response_data.get('lesion_locations'):
        response_data['lesion_locations'] = json.loads(response_data['lesion_locations'])
    else:
        response_data['lesion_locations'] = []
    
    return response_data


@router.get("/", response_model=SymptomResponse)
async def get_symptoms(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: HealthcareWorker = Depends(get_current_user)
):
    """
    Get symptoms for a case.
    """
    
    # 1. Validate case exists and belongs to user
    case = db.query(PatientCase).filter(
        PatientCase.case_id == case_id,
        PatientCase.worker_id == current_user.user_id
    ).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # 2. Get symptoms
    symptom = db.query(Symptom).filter(
        Symptom.case_id == case.id
    ).first()
    
    if not symptom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No symptoms found for this case"
        )
    
    # Convert locations back to list for response
    response_data = symptom.__dict__.copy()
    if response_data.get('lesion_locations'):
        response_data['lesion_locations'] = json.loads(response_data['lesion_locations'])
    else:
        response_data['lesion_locations'] = []
    
    return response_data


@router.put("/", response_model=SymptomResponse)
async def update_symptoms(
    case_id: str,
    symptom_data: SymptomCreate,
    db: Session = Depends(get_db),
    current_user: HealthcareWorker = Depends(get_current_user)
):
    """
    Update symptoms for a case (alias for POST).
    """
    return await create_symptoms(case_id, symptom_data, db, current_user)


@router.delete("/")
async def delete_symptoms(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: HealthcareWorker = Depends(get_current_user)
):
    """
    Delete symptoms for a case.
    """
    
    # 1. Validate case exists and belongs to user
    case = db.query(PatientCase).filter(
        PatientCase.case_id == case_id,
        PatientCase.worker_id == current_user.user_id
    ).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # 2. Get symptoms
    symptom = db.query(Symptom).filter(
        Symptom.case_id == case.id
    ).first()
    
    if not symptom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No symptoms found for this case"
        )
    
    db.delete(symptom)
    db.commit()
    
    return {"message": "Symptoms deleted successfully"}