import os
import boto3
import io
from botocore.exceptions import ClientError
from typing import List, Dict, Any
import numpy as np

# Lazy load TF so it doesn't slow down every import
tf = None

class MLModelService:
    _instance = None
    _model = None
    _classes = ["Eczema", "Leishmaniasis", "Tinea", "others"]
    _image_size = (300, 300)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLModelService, cls).__new__(cls)
        return cls._instance

    def _load_model(self) -> bool:
        global tf
        if tf is None:
            import tensorflow as tf
        
        if self._model is None:
            # Construct absolute path to the model relative to this file
            # This file is in backend/app/services/
            # Model is in ml_efficientnet_v2/artifacts/models/efficientnet_final.keras
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
            model_path = os.path.join(project_root, "ml_efficientnet_v2", "artifacts", "models", "efficientnet_final.keras")
            
            if not os.path.exists(model_path):
                print(f"WARNING: ML model file not found at {model_path}. Please train the model first.")
                return False
                
            self._model = tf.keras.models.load_model(model_path)
        return True
    
    def _preprocess_image_bytes(self, image_bytes: bytes) -> np.ndarray:
        """Preprocess an image from bytes for the model."""
        global tf
        if tf is None:
            import tensorflow as tf
            
        try:
            # Use TF's io to decode
            img = tf.io.decode_image(image_bytes, channels=3, expand_animations=False)
            img = tf.image.resize(img, self._image_size)
            img_array = tf.keras.utils.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0) # Create batch axis
            return img_array
        except Exception as e:
            raise ValueError(f"Failed to preprocess image bytes: {e}")

    def predict_from_s3_keys(self, s3_keys: List[str], s3_bucket: str) -> Dict[str, float]:
        """
        Download images from S3 (into memory) and predict.
        Returns the aggregated probabilities for each target class in percentage.
        """
        if not self._load_model():
            # Fallback if the model isn't trained yet
            return {
                "Eczema": 33.34,
                "Leishmaniasis": 33.33,
                "Tinea": 33.33
            }
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "AKIA4TWFKL6LLXXYKUOM"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "S4SAGSgqFmGDDm6HCubupG7raekoQwoGXy1HJEL"),
            region_name=os.getenv("AWS_REGION", "ap-southeast-1")
        )
        
        valid_predictions = []
        
        for key in s3_keys:
            try:
                # Download to bytes directly in memory
                response = s3_client.get_object(Bucket=s3_bucket, Key=key)
                image_bytes = response['Body'].read()
                
                # Preprocess
                img_array = self._preprocess_image_bytes(image_bytes)
                
                # Predict
                predictions = self._model.predict(img_array, verbose=0)[0]
                results = {class_name: float(prob) for class_name, prob in zip(self._classes, predictions)}
                
                # Extract probabilities for the 3 target classes, ignoring "others"
                valid_predictions.append([results["Eczema"], results["Leishmaniasis"], results["Tinea"]])
                
            except Exception as e:
                print(f"Error predicting image {key}: {e}")
        
        if not valid_predictions:
            # Fallback if all S3 fails
            return {
                "Eczema": 0.0,
                "Leishmaniasis": 0.0,
                "Tinea": 0.0
            }
            
        # Mean probability aggregation over the 3 target classes
        mean_probs = np.mean(valid_predictions, axis=0)
        
        # Normalize the probabilities so they sum to 1.0
        total = np.sum(mean_probs)
        if total > 0:
            normalized_probs = mean_probs / total
        else:
            normalized_probs = mean_probs
            
        return {
            "Eczema": float(normalized_probs[0]) * 100,
            "Leishmaniasis": float(normalized_probs[1]) * 100,
            "Tinea": float(normalized_probs[2]) * 100
        }

# Singleton instance
ml_service = MLModelService()
