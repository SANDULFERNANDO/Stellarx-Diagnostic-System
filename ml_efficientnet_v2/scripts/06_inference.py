import os
import sys
import numpy as np
import tensorflow as tf
from pathlib import Path
from PIL import Image

# Add src to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.data_utils import load_config

class StellarXPredictor:
    def __init__(self, model_path, config_path):
        self.config = load_config(config_path)
        self.classes = self.config["classes"]
        self.image_size = tuple(self.config["image_size"])
        self.model = tf.keras.models.load_model(model_path)
        
    def _preprocess_image(self, image_path):
        """Validates and preprocesses a single image."""
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
            
        try:
            img = tf.keras.utils.load_img(image_path, target_size=self.image_size)
            img_array = tf.keras.utils.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0) # Create batch axis
            return img_array
        except Exception as e:
            raise ValueError(f"Unsupported or corrupted image file: {e}")

    def predict_single_image(self, image_path):
        """Predicts the probabilities for a single image."""
        img_array = self._preprocess_image(image_path)
        
        # Predict
        predictions = self.model.predict(img_array, verbose=0)[0]
        
        # Format results
        results = {class_name: float(prob) for class_name, prob in zip(self.classes, predictions)}
        top_class = self.classes[np.argmax(predictions)]
        
        return {
            "top_prediction": top_class,
            "probabilities": results,
            "is_rejected": (top_class == "others")
        }

    def predict_case_images(self, image_paths):
        """
        Aggregates predictions for 1-5 images belonging to the SAME patient case.
        Uses Prototype mean-probability case-level aggregation.
        """
        if not (1 <= len(image_paths) <= 5):
            raise ValueError("A case must contain between 1 and 5 images.")
            
        valid_predictions = []
        individual_results = {}
        
        for path in image_paths:
            try:
                res = self.predict_single_image(path)
                individual_results[str(path)] = res
                
                # We only aggregate probabilities if the image wasn't rejected as 'Others'
                if not res["is_rejected"]:
                    valid_predictions.append(list(res["probabilities"].values()))
            except Exception as e:
                individual_results[str(path)] = {"error": str(e)}
                
        # Aggregate
        if not valid_predictions:
            # All uploaded images were rejected as non-clinical
            return {
                "final_case_prediction": "Unsupported image / Unable to confidently classify",
                "aggregated_probabilities": None,
                "individual_image_results": individual_results,
                "message": "All images in this case were flagged as non-clinical (Others)."
            }
            
        # Mean probability aggregation
        mean_probs = np.mean(valid_predictions, axis=0)
        final_class = self.classes[np.argmax(mean_probs)]
        
        agg_results = {class_name: float(prob) for class_name, prob in zip(self.classes, mean_probs)}
        
        return {
            "final_case_prediction": final_class,
            "aggregated_probabilities": agg_results,
            "individual_image_results": individual_results,
            "message": "Prototype mean-probability case-level aggregation successful."
        }

# Example Usage
if __name__ == "__main__":
    workspace_dir = Path(__file__).resolve().parent.parent
    model_path = workspace_dir / "artifacts" / "models" / "efficientnet_final.keras"
    config_path = workspace_dir / "config" / "training_config.json"
    
    if model_path.exists():
        predictor = StellarXPredictor(model_path, config_path)
        print("StellarXPredictor initialized successfully.")
    else:
        print("Model not found. Please train it first.")
