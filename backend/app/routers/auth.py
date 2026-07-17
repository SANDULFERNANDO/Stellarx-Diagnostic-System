import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app import models, schemas, auth_utils

router = APIRouter(prefix="/auth", tags=["Authentication"])

MAX_FAILED_ATTEMPTS = 5
LOCK_DURATION_MINUTES = 15


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserRegister, db: DBSession = Depends(get_db)):
    existing = db.query(models.HealthcareWorker).filter(
        (models.HealthcareWorker.email == user.email) |
        (models.HealthcareWorker.username == user.username)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email or username already registered")

    new_user = models.HealthcareWorker(
        username=user.username,
        first_name=user.firstName,
        last_name=user.lastName,
        email=user.email,
        phone=user.phone,
        password_hash=auth_utils.hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: DBSession = Depends(get_db)):
    user = db.query(models.HealthcareWorker).filter(
        models.HealthcareWorker.email == credentials.email
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=423,
            detail=f"Account locked until {user.locked_until.isoformat()}"
        )

    if not auth_utils.verify_password(credentials.password, user.password_hash):
        user.failed_attempts += 1
        if user.failed_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOCK_DURATION_MINUTES)
        db.commit()
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    user.failed_attempts = 0
    user.locked_until = None
    db.commit()

    access_token = auth_utils.create_access_token(data={"sub": str(user.user_id)})

    session_record = models.Session(
        session_id=str(uuid.uuid4()),
        user_id=user.user_id,
        token=access_token,
        expires_at=datetime.utcnow() + timedelta(minutes=auth_utils.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    db.add(session_record)
    db.commit()

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(
    token: str = Depends(auth_utils.oauth2_scheme),
    db: DBSession = Depends(get_db)
):
    session_record = db.query(models.Session).filter(models.Session.token == token).first()
    if session_record:
        db.delete(session_record)
        db.commit()
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=schemas.UserOut)
def get_me(
    current_user_id: int = Depends(auth_utils.get_current_user_id),
    db: DBSession = Depends(get_db)
):
    user = db.query(models.HealthcareWorker).filter(
        models.HealthcareWorker.user_id == current_user_id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user