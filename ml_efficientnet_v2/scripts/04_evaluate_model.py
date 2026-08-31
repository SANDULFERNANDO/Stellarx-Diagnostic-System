import os
import sys
import numpy as np
import tensorflow as tf
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.data_utils import create_dataset, load_config
from src.evaluation_utils import generate_full_evaluation_report

def main():
    workspace_dir = Path(__file__).resolve().parent.parent
    config_path = workspace_dir / "config" / "training_config.json"
    processed_data_dir = workspace_dir / "processed_data"
    model_path = workspace_dir / "artifacts" / "models" / "efficientnet_final.keras"
    metrics_dir = workspace_dir / "artifacts" / "metrics"
    
    if not model_path.exists():
        print(f"Error: Model not found at {model_path}. Please train the model first.")
        return
        
    print("Loading configuration...")
    config = load_config(config_path)
    classes = config["classes"]
    
    print("Loading test dataset (No Augmentation)...")
    # Strictly load only the TEST dataset, with augment=False
    test_ds = create_dataset(processed_data_dir / "test", config, "test", augment=False)
    
    print("Loading model...")
    model = tf.keras.models.load_model(str(model_path))
    
    print("Generating predictions on the untouched test set...")
    # Gather true labels and predictions
    y_true = []
    y_pred_probs = []
    
    for images, labels in test_ds:
        # Convert one-hot to integer labels
        y_true.extend(np.argmax(labels.numpy(), axis=1))
        
        # Predict
        preds = model.predict(images, verbose=0)
        y_pred_probs.extend(preds)
        
    y_true = np.array(y_true)
    y_pred_probs = np.array(y_pred_probs)
    y_pred = np.argmax(y_pred_probs, axis=1)
    
    print("Computing metrics and generating reports...")
    generate_full_evaluation_report(y_true, y_pred, classes, metrics_dir)

if __name__ == "__main__":
    main()
