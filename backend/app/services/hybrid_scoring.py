import random
import json
from typing import Dict, Any

def mock_image_prediction(case_id: str) -> Dict[str, float]:
    """
    Mock image prediction function for testing hybrid pipeline.
    Randomly generates probabilities for the three target diseases.
    """
    # Seed randomly using case_id string so it's deterministic per case
    random.seed(case_id)
    
    # Generate random raw scores
    raw_scores = {
        "Tinea Infection": random.uniform(0.1, 0.9),
        "Leishmaniasis": random.uniform(0.1, 0.9),
        "Eczema": random.uniform(0.1, 0.9)
    }
    
    # Normalize to 1.0
    total = sum(raw_scores.values())
    normalized = {k: round((v / total) * 100, 2) for k, v in raw_scores.items()}
    
    return normalized

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
