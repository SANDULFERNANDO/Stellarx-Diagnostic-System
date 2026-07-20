from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


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

    session_id  = Column(String(36), primary_key=True)
    user_id     = Column(Integer, nullable=False)
    token       = Column(String(500), nullable=False)
    expires_at  = Column(DateTime, nullable=False)
    created_at  = Column(DateTime, server_default=func.now())


class PatientCase(Base):
    __tablename__ = "patient_cases"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String(20), unique=True, index=True, nullable=False)
    worker_id = Column(Integer, nullable=False, index=True)  # FK to HealthcareWorker
    case_date = Column(Date, nullable=False)
    patient_age = Column(Integer, nullable=True)
    patient_gender = Column(String(10), nullable=True)
    patient_location = Column(String(255), nullable=True)
    status = Column(String(20), default="DRAFT")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())