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

# =====================================================
# REGISTER (Unchanged)
# =====================================================

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


# =====================================================
# LOGIN (UPDATED WITH ACCOUNT LOCKING)
# =====================================================

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    # 1. Get user by email
    db_user = db.query(HealthcareWorker).filter(HealthcareWorker.email == user.email).first()
    
    # 2. Check if user exists
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # 3. Check if account is locked
    if db_user.locked_until and db_user.locked_until > datetime.now():
        # Calculate remaining lock time
        remaining_seconds = int((db_user.locked_until - datetime.now()).total_seconds())
        remaining_minutes = remaining_seconds // 60
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked. Please try again in {remaining_minutes} minute(s)."
        )
    
    # 4. Verify password
    if not verify_password(user.password, db_user.password_hash):
        # Increment failed attempts
        db_user.failed_attempts += 1
        
        # Lock account after 3 failed attempts
        if db_user.failed_attempts >= 3:
            db_user.locked_until = datetime.now() + timedelta(minutes=15)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account locked due to multiple failed attempts. Please try again after 15 minutes."
            )
        
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid credentials. {3 - db_user.failed_attempts} attempt(s) remaining."
        )
    
    # 5. Successful login – Reset failed attempts and locked_until
    db_user.failed_attempts = 0
    db_user.locked_until = None
    db.commit()
    
    # 6. Generate token
    token = create_access_token(data={"sub": str(db_user.user_id)})
    return {"access_token": token, "token_type": "bearer"}


# =====================================================
# GET CURRENT USER (Unchanged)
# =====================================================

@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: HealthcareWorker = Depends(get_current_user)):
    return current_user


# =====================================================
# FORGOT PASSWORD (FR-11)
# =====================================================

@router.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(HealthcareWorker).filter(HealthcareWorker.email == email).first()
    if not user:
        return {"message": "If your email is registered, you will receive a reset link."}
    
    reset_token = create_access_token(
        data={"sub": str(user.user_id), "type": "reset"},
        expires_delta=timedelta(minutes=30)
    )
    
    new_session = SessionModel(
        user_id=user.user_id,
        token=reset_token,
        expires_at=datetime.now() + timedelta(minutes=30)
    )
    db.add(new_session)
    db.commit()
    
    return {
        "message": "Password reset link sent to your email.",
        "reset_token": reset_token
    }


# =====================================================
# RESET PASSWORD (FR-11)
# =====================================================

@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    token_type = payload.get("type")
    if token_type != "reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type"
        )
    
    user_id = payload.get("sub")
    
    session_record = db.query(SessionModel).filter(
        SessionModel.token == token,
        SessionModel.expires_at > datetime.now()
    ).first()
    
    if not session_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user = db.query(HealthcareWorker).filter(
        HealthcareWorker.user_id == user_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.password_hash = get_password_hash(new_password)
    db.delete(session_record)
    db.commit()
    
    return {"message": "Password reset successfully. Please login with your new password."}


# =====================================================
# CHANGE PASSWORD (FR-14)
# =====================================================

@router.post("/change-password")
def change_password(
    current_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: HealthcareWorker = Depends(get_current_user)
):
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )
    
    current_user.password_hash = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


# =====================================================
# DELETE PROFILE (FR-34)
# =====================================================

@router.delete("/profile")
def delete_profile(
    password: str,
    db: Session = Depends(get_db),
    current_user: HealthcareWorker = Depends(get_current_user)
):
    if not verify_password(password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    db.delete(current_user)
    db.commit()
    
    return {"message": "Account deleted successfully"}