# backend/app/routers/images.py
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

from app.database import get_db
from app.models import PatientCase, Image, HealthcareWorker
from app.auth_utils import get_current_user
from app.services.image_validation import ImageQualityValidator

router = APIRouter(prefix="/cases/{case_id}/images", tags=["Images"])
quality_validator = ImageQualityValidator()

# Initialize S3 Client
# We use os.getenv to pull from the .env file variables, OR hardcode directly if preferred.
# Since the .env file has these variables, it's best to pull them by their variable names:
S3_BUCKET = os.getenv("AWS_S3_BUCKET_NAME", "stellarx-images-sandul")
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "AKIA4TWFKL6LLXXYKUOM"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "S4SAGSgqFmGDDm6HCubupG7raekoQwoGXy1HJEL"),
    region_name=os.getenv("AWS_REGION", "ap-southeast-1")  # Make sure this matches your actual bucket region
)


@router.post("/")
async def upload_images(
    case_id: str,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: HealthcareWorker = Depends(get_current_user)
):
    """
    Upload 1-5 clinical images for a case.
    Each image is validated for quality (blur, brightness, contrast, resolution).
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

        # 4c. ✅ IMAGE QUALITY VALIDATION
        file.file.seek(0)
        image_bytes = await file.read()
        file.file.seek(0)

        quality_result = quality_validator.validate(image_bytes)
        print(f"🔍 Quality check for {file.filename}: score={quality_result['quality_score']}, issues={quality_result['issues']}")

        if not quality_result['is_valid'] or quality_result['quality_score'] < 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image quality too low for {file.filename}: {', '.join(quality_result['issues'])}"
            )

        # 4d. Generate unique S3 key
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        s3_key = f"cases/{case_id}/image_{index}_{uuid.uuid4()}.{file_extension}"

        # 4e. Upload to AWS S3
        file.file.seek(0)
        try:
            s3_client.upload_fileobj(
                file.file,
                S3_BUCKET,
                s3_key,
                ExtraArgs={'ContentType': file.content_type}
            )
        except ClientError as e:
            print(f"S3 Upload Error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload {file.filename} to S3"
            )
        finally:
            file.file.seek(0)

        # Generate presigned URL for response
        try:
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET, 'Key': s3_key},
                ExpiresIn=3600
            )
        except ClientError:
            presigned_url = None

        # 4f. Save to database
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
            "url": presigned_url
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
    """Get all images for a case, returning presigned S3 URLs"""
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
    
    result_images = []
    for img in images:
        try:
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET, 'Key': img.s3_key},
                ExpiresIn=3600
            )
        except ClientError:
            url = None
            
        result_images.append({
            "id": img.id,
            "file_name": img.file_name,
            "s3_key": img.s3_key,
            "image_index": img.image_index,
            "uploaded_at": img.uploaded_at,
            "url": url
        })

    return {
        "success": True,
        "case_id": case_id,
        "images": result_images,
        "total": len(images)
    }


@router.delete("/{image_id}")
async def delete_image(
    case_id: str,
    image_id: str,
    db: Session = Depends(get_db),
    current_user: HealthcareWorker = Depends(get_current_user)
):
    """Delete a specific image from S3 and Database"""
    case = db.query(PatientCase).filter(
        PatientCase.case_id == case_id,
        PatientCase.worker_id == current_user.user_id
    ).first()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )

    image = db.query(Image).filter(
        Image.id == image_id,
        Image.case_id == case.id
    ).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    # 1. Delete from S3
    try:
        s3_client.delete_object(
            Bucket=S3_BUCKET,
            Key=image.s3_key
        )
    except ClientError as e:
        print(f"Error deleting object from S3: {e}")
        # Proceed to delete from DB anyway so we don't have zombie records

    # 2. Delete from database
    db.delete(image)
    db.commit()

    return {
        "success": True,
        "message": "Image deleted successfully"
    }