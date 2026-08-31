import random
import json
from typing import Dict, Any

from app.services.ml_inference import ml_service
import os

def get_real_image_prediction(s3_keys: list) -> Dict[str, float]:
    """
    Get real image predictions from the TensorFlow model using S3 images.
    Maps the ML classes to match the symptom model expectations.
    """
    if not s3_keys:
        return {
            "Tinea Infection": 33.33,
            "Leishmaniasis": 33.33,
            "Eczema": 33.34
        }
        
    s3_bucket = os.getenv("AWS_S3_BUCKET_NAME", "stellarx-images-sandul")
    ml_probs = ml_service.predict_from_s3_keys(s3_keys, s3_bucket)
    
    # Map ML classes to expected keys
    mapped_probs = {
        "Eczema": ml_probs.get("Eczema", 0.0),
        "Leishmaniasis": ml_probs.get("Leishmaniasis", 0.0),
        "Tinea Infection": ml_probs.get("Tinea", 0.0)
    }
    
    return mapped_probs

def fuse_predictions(symptom_probs: Dict[str, float], image_probs: Dict[str, float]) -> Dict[str, Any]:
    """
    Fuses symptom and image predictions using a 30/70 weighted average.
    (30% Symptom Model, 70% Image Inference)
    Returns the fused probabilities and the final top diagnosis.
    """
    fused_probs = {}
    
    for condition in ["Tinea Infection", "Leishmaniasis", "Eczema"]:
        symptom_score = symptom_probs.get(condition, 0.0)
        image_score = image_probs.get(condition, 0.0)
        
        # 30% symptom, 70% image
        fused_score = (symptom_score * 0.3) + (image_score * 0.7)
        fused_probs[condition] = round(fused_score, 2)
        
    # Find the top diagnosis
    top_condition = max(fused_probs.items(), key=lambda x: x[1])
    
    return {
        "final_probabilities": fused_probs,
        "final_diagnosis": top_condition[0],
        "final_confidence": top_condition[1]
    }
