# backend/app/routers/images.py
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
import os
from datetime import datetime

from app.database import get_db
from app.models import PatientCase, Image, HealthcareWorker
from app.auth_utils import get_current_user

# Create router
router = APIRouter(prefix="/cases/{case_id}/images", tags=["Images"])


@router.post("/")
async def upload_images(
    case_id: str,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: HealthcareWorker = Depends(get_current_user)
):
    """
    Upload 1-5 clinical images for a case.
    Max 5 images per request.
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
    
    # 2. Validate number of images (1-5)
    if len(files) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 1 image is required"
        )
    
    if len(files) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 images allowed"
        )
    
    # 3. Check existing images count
    existing_images = db.query(Image).filter(Image.case_id == case.id).count()
    
    if existing_images + len(files) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Case already has {existing_images} images. Maximum 5 allowed."
        )
    
    # 4. Upload each file
    uploaded_images = []
    
    for index, file in enumerate(files):
        # 4a. Validate file type
        if file.content_type not in ["image/jpeg", "image/png", "image/jpg", "image/webp"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type: {file.filename}. Only JPG, PNG, WEBP allowed."
            )
        
        # 4b. Validate file size (max 5MB)
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large: {file.filename}. Max 5MB."
            )
        
        # 4c. Generate unique S3 key
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        s3_key = f"cases/{case_id}/image_{index}_{uuid.uuid4()}.{file_extension}"
        
        # 4d. For now, store locally (since S3 is not fully configured yet)
        # TODO: Replace with S3 upload when AWS is configured
        local_path = f"uploads/{case_id}"
        os.makedirs(local_path, exist_ok=True)
        local_file_path = f"{local_path}/{s3_key.split('/')[-1]}"
        
        with open(local_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 4e. Save to database
        new_image = Image(
            id=str(uuid.uuid4()),
            case_id=case.id,
            s3_key=s3_key,
            file_name=file.filename,
            file_size=file_size,
            content_type=file.content_type,
            image_index=existing_images + index
        )
        
        db.add(new_image)
        uploaded_images.append({
            "id": new_image.id,
            "file_name": file.filename,
            "s3_key": s3_key,
            "image_index": new_image.image_index,
            "local_path": local_file_path
        })
    
    # 5. Commit all changes
    db.commit()
    
    return {
        "success": True,
        "message": f"Successfully uploaded {len(files)} image(s)",
        "case_id": case_id,
        "uploaded_images": uploaded_images,
        "total_images": existing_images + len(files)
    }


@router.get("/")
async def get_images(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: HealthcareWorker = Depends(get_current_user)
):
    """Get all images for a case"""
    
    # Validate case exists
    case = db.query(PatientCase).filter(
        PatientCase.case_id == case_id,
        PatientCase.worker_id == current_user.user_id
    ).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    images = db.query(Image).filter(Image.case_id == case.id).order_by(Image.image_index).all()
    
    return {
        "success": True,
        "case_id": case_id,
        "images": [
            {
                "id": img.id,
                "file_name": img.file_name,
                "s3_key": img.s3_key,
                "image_index": img.image_index,
                "uploaded_at": img.uploaded_at
            }
            for img in images
        ],
        "total": len(images)
    }


@router.delete("/{image_id}")
async def delete_image(
    case_id: str,
    image_id: str,
    db: Session = Depends(get_db),
    current_user: HealthcareWorker = Depends(get_current_user)
):
    """Delete a specific image"""
    
    # Validate case exists
    case = db.query(PatientCase).filter(
        PatientCase.case_id == case_id,
        PatientCase.worker_id == current_user.user_id
    ).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Find the image
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.case_id == case.id
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Delete from database
    db.delete(image)
    db.commit()
    
    return {
        "success": True,
        "message": "Image deleted successfully"
    }