import os
import sys
from pathlib import Path
import random
import tensorflow as tf

# Add src to Python path
workspace_dir = Path(__file__).resolve().parent.parent
import importlib.util
spec = importlib.util.spec_from_file_location("generate_gradcam", str(workspace_dir / "scripts" / "05_generate_gradcam.py"))
generate_gradcam = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_gradcam)
get_img_array = generate_gradcam.get_img_array
make_gradcam_heatmap = generate_gradcam.make_gradcam_heatmap
save_and_display_gradcam = generate_gradcam.save_and_display_gradcam

from src.data_utils import load_config

def main():
    config_path = workspace_dir / "config" / "training_config.json"
    model_path = workspace_dir / "artifacts" / "models" / "efficientnet_final.keras"
    test_dir = workspace_dir / "processed_data" / "test"
    output_dir = workspace_dir / "artifacts" / "explainability"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not model_path.exists():
        print("Error: Model not found.")
        return
        
    print("Loading config and model...")
    config = load_config(config_path)
    classes = config["classes"]
    img_size = tuple(config["image_size"])
    model = tf.keras.models.load_model(str(model_path))
    
    backbone = model.layers[1]
    last_conv_layer_name = "efficientnetb3"
    
    print("Generating Grad-CAM heatmaps for one sample from each class...")
    
    for class_name in classes:
        class_dir = test_dir / class_name
        if not class_dir.exists():
            continue
            
        images = [f for f in os.listdir(class_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not images:
            continue
            
        # Select a random image
        sample_img = class_dir / images[0]
        
        # Preprocess
        img_array = get_img_array(str(sample_img), size=img_size)
        
        # Predict
        preds = model.predict(img_array, verbose=0)
        pred_idx = tf.argmax(preds[0]).numpy()
        pred_class = classes[pred_idx]
        
        # Generate heatmap
        heatmap = make_gradcam_heatmap(img_array, model, last_conv_layer_name)
        
        # Save superimposed image
        output_name = f"gradcam_{class_name}_pred_{pred_class}.png"
        output_path = output_dir / output_name
        save_and_display_gradcam(str(sample_img), heatmap, str(output_path))
        print(f"[{class_name}] True: {class_name} | Predicted: {pred_class} -> Saved to {output_name}")

if __name__ == "__main__":
    main()
