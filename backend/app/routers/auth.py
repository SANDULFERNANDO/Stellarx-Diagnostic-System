from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models import HealthcareWorker, Session as SessionModel
from app.schemas import UserRegister, UserLogin, Token, UserOut
from app.auth_utils import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    verify_token
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut)
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(HealthcareWorker).filter(HealthcareWorker.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = HealthcareWorker(
        username=user.username,
        email=user.email,
        password_hash=get_password_hash(user.password),
        first_name=user.firstName,
        last_name=user.lastName,
        phone=user.phone
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(HealthcareWorker).filter(HealthcareWorker.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": str(db_user.user_id)})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: HealthcareWorker = Depends(get_current_user)):
    return current_user


# =====================================================
# ✅ NEW: Password Reset Endpoints (FR-11)
# =====================================================

@router.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    """
    Step 1: Request password reset.
    Generates a reset token and stores it in sessions table.
    """
    # Find user by email
    user = db.query(HealthcareWorker).filter(HealthcareWorker.email == email).first()
    
    # Security: Don't reveal if email exists
    if not user:
        return {"message": "If your email is registered, you will receive a reset link."}
    
    # Generate reset token (valid for 30 minutes)
    reset_token = create_access_token(
        data={"sub": str(user.user_id), "type": "reset"},
        expires_delta=timedelta(minutes=30)
    )
    
    # Store token in sessions table for validation
    new_session = SessionModel(
        user_id=user.user_id,
        token=reset_token,
        expires_at=datetime.now() + timedelta(minutes=30)
    )
    db.add(new_session)
    db.commit()
    
    # TODO: Send email with reset link (will be added later)
    # For now, return token for testing
    
    return {
        "message": "Password reset link sent to your email.",
        "reset_token": reset_token  # Remove this in production
    }


@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    """
    Step 2: Reset password using token.
    Validates token and updates password.
    """
    # Validate token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Check token type
    token_type = payload.get("type")
    if token_type != "reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type"
        )
    
    user_id = payload.get("sub")
    
    # Check token exists in sessions table
    session_record = db.query(SessionModel).filter(
        SessionModel.token == token,
        SessionModel.expires_at > datetime.now()
    ).first()
    
    if not session_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Get user
    user = db.query(HealthcareWorker).filter(
        HealthcareWorker.user_id == user_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.password_hash = get_password_hash(new_password)
    
    # Delete used token (one-time use)
    db.delete(session_record)
    db.commit()
    
    return {"message": "Password reset successfully. Please login with your new password."}