from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime

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