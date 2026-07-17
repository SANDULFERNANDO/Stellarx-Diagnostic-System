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