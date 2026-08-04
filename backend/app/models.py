# backend/app/models.py
import uuid
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Float, Text  # ← ADD Float, Text
from sqlalchemy.sql import func
from app.database import Base

# =====================================================
# AUTH MODELS
# =====================================================

class HealthcareWorker(Base):
    __tablename__ = "healthcare_workers"

    user_id         = Column(Integer, primary_key=True, autoincrement=True)
    username        = Column(String(50), nullable=False, unique=True)
    password_hash   = Column(String(255), nullable=False)
    email           = Column(String(100), nullable=False, unique=True)
    phone           = Column(String(20), nullable=True)
    first_name      = Column(String(50), nullable=False)
    last_name       = Column(String(50), nullable=False)
    is_active       = Column(Boolean, nullable=False, default=True)
    failed_attempts = Column(Integer, nullable=False, default=0)
    locked_until    = Column(DateTime, nullable=True)
    created_at      = Column(DateTime, server_default=func.now())
    updated_at      = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Session(Base):
    __tablename__ = "sessions"
    
    session_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # ✅ Auto-generate UUID
    user_id = Column(Integer, nullable=False)
    token = Column(String(500), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

# =====================================================
# CASE MODEL
# =====================================================

class PatientCase(Base):
    __tablename__ = "patient_cases"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String(20), unique=True, index=True, nullable=False)
    worker_id = Column(Integer, nullable=False, index=True)
    case_date = Column(Date, nullable=False)
    patient_age = Column(Integer, nullable=True)
    patient_gender = Column(String(10), nullable=True)
    patient_location = Column(String(255), nullable=True)
    status = Column(String(20), default="DRAFT")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# =====================================================
# IMAGE MODEL (ADD THIS)
# =====================================================

class Image(Base):
    __tablename__ = "images"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String(36), nullable=False, index=True)
    s3_key = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(100), nullable=False)
    image_index = Column(Integer, nullable=False, default=0)
    uploaded_at = Column(DateTime, server_default=func.now())

# =====================================================
# SYMPTOM MODEL (ADD THIS)
# =====================================================

class Symptom(Base):
    __tablename__ = "symptoms"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String(36), nullable=False, unique=True, index=True)
    
    # Basic Symptoms
    redness = Column(Boolean, default=False)
    scaling = Column(Boolean, default=False)
    ring_shaped = Column(Boolean, default=False)
    itching = Column(Boolean, default=False)
    pain = Column(Boolean, default=False)
    
    # Duration & Severity
    duration_value = Column(Integer, nullable=True)
    duration_unit = Column(String(20), nullable=True)  # days, weeks, months
    itch_severity = Column(Integer, nullable=True)  # 1-10
    
    # Lesion Characteristics
    lesion_size_cm = Column(Float, nullable=True)
    lesion_border = Column(String(50), nullable=True)  # well_defined, ill_defined, irregular
    lesion_shape = Column(String(50), nullable=True)  # circular, irregular, multiple
    lesion_color = Column(String(50), nullable=True)  # red, pink, brown, silver_white, dark
    
    # Lesion Location (stored as comma-separated or JSON)
    lesion_locations = Column(String(255), nullable=True)  # arms, legs, face, etc.
    
    # Additional Clinical Signs
    central_clearing = Column(Boolean, default=False)
    previous_treatment = Column(String(50), nullable=True)  # none, topical_steroid, etc.
    nail_changes = Column(Boolean, default=False)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Audit
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())