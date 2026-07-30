# backend/app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime


# =====================================================
# AUTH SCHEMAS
# =====================================================

class UserRegister(BaseModel):
    username: str
    firstName: str
    lastName: str
    email: EmailStr
    phone: Optional[str] = None
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    user_id: int
    username: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# =====================================================
# CASE SCHEMAS
# =====================================================

class CaseCreate(BaseModel):
    patient_age: int
    patient_gender: str
    patient_location: str


class CaseResponse(BaseModel):
    case_id: str
    worker_id: int
    case_date: date
    patient_age: int
    patient_gender: str
    patient_location: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class CaseUpdate(BaseModel):
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    patient_location: Optional[str] = None


# =====================================================
# SYMPTOM SCHEMAS
# =====================================================

class SymptomCreate(BaseModel):
    redness: bool = False
    scaling: bool = False
    ring_shaped: bool = False
    itching: bool = False
    pain: bool = False

    duration_value: Optional[int] = None
    duration_unit: Optional[str] = None
    itch_severity: Optional[int] = None

    lesion_size_cm: Optional[float] = None
    lesion_border: Optional[str] = None
    lesion_shape: Optional[str] = None
    lesion_color: Optional[str] = None
    lesion_locations: Optional[List[str]] = None

    central_clearing: bool = False
    previous_treatment: Optional[str] = None
    nail_changes: bool = False

    notes: Optional[str] = None


class SymptomResponse(BaseModel):
    id: str
    case_id: str

    redness: bool
    scaling: bool
    ring_shaped: bool
    itching: bool
    pain: bool

    duration_value: Optional[int] = None
    duration_unit: Optional[str] = None
    itch_severity: Optional[int] = None

    lesion_size_cm: Optional[float] = None
    lesion_border: Optional[str] = None
    lesion_shape: Optional[str] = None
    lesion_color: Optional[str] = None
    lesion_locations: Optional[List[str]] = None

    central_clearing: bool
    previous_treatment: Optional[str] = None
    nail_changes: bool

    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# REBUILD (fixes Pydantic forward-reference issues)
# =====================================================

SymptomCreate.model_rebuild()
SymptomResponse.model_rebuild()
CaseCreate.model_rebuild()
CaseResponse.model_rebuild()