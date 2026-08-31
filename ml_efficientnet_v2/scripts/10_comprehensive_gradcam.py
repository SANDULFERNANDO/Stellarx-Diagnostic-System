import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pathlib import Path
import tensorflow as tf

def make_gradcam_heatmap(img_array, model, last_conv_layer_name, pred_index=None):
    backbone = model.layers[1] 
    
    # 1. Feature extractor model
    feature_model = tf.keras.models.Model(backbone.inputs, backbone.output)
    
    # 2. Classification head model
    classifier_input = tf.keras.Input(shape=backbone.output.shape[1:])
    x = classifier_input
    for layer in model.layers[2:]:
        x = layer(x)
    classifier_model = tf.keras.models.Model(classifier_input, x)
    
    with tf.GradientTape() as tape:
        last_conv_layer_output = feature_model(img_array)
        tape.watch(last_conv_layer_output)
        
        preds = classifier_model(last_conv_layer_output)
        if pred_index is None:
            pred_index = tf.argmax(preds[0])
        class_channel = preds[:, pred_index]

    grads = tape.gradient(class_channel, last_conv_layer_output)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    last_conv_layer_output = last_conv_layer_output[0]
    heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
    return heatmap.numpy()

def generate_composite_image(img_path, heatmap, true_class, pred_class, confidence, output_path, img_size=(300, 300)):
    # 1. Original Image
    img = tf.keras.preprocessing.image.load_img(img_path, target_size=img_size)
    img = tf.keras.preprocessing.image.img_to_array(img)
    
    # 2. Heatmap processing
    heatmap_uint8 = np.uint8(255 * heatmap)
    jet = plt.get_cmap("jet")
    jet_colors = jet(np.arange(256))[:, :3]
    jet_heatmap = jet_colors[heatmap_uint8]
    jet_heatmap = tf.keras.preprocessing.image.array_to_img(jet_heatmap)
    jet_heatmap = jet_heatmap.resize(img_size)
    jet_heatmap = tf.keras.preprocessing.image.img_to_array(jet_heatmap)
    
    # 3. Superimposed
    superimposed_img = jet_heatmap * 0.4 + img
    superimposed_img = tf.keras.preprocessing.image.array_to_img(superimposed_img)
    
    # Create Figure
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    
    # Main Title (Explainability Disclaimer)
    fig.suptitle(f"Explainability (Feature Attribution) - EfficientNetB3\n"
                 f"Actual: {true_class} | Predicted: {pred_class} (Confidence: {confidence:.2%})\n"
                 f"(Note: Heatmaps show regions that mathematically contributed to the prediction, not clinical lesion segmentation)", 
                 fontsize=14, y=1.05)
    
    # Plot 1: Original
    axes[0].imshow(img / 255.0)
    axes[0].set_title("1. Original Image", fontsize=12)
    axes[0].axis('off')
    
    # Plot 2: Heatmap Only
    axes[1].imshow(jet_heatmap / 255.0)
    axes[1].set_title("2. Grad-CAM Heatmap", fontsize=12)
    axes[1].axis('off')
    
    # Plot 3: Overlay
    axes[2].imshow(superimposed_img)
    axes[2].set_title("3. Heatmap Overlay", fontsize=12)
    axes[2].axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def main():
    workspace_dir = Path(__file__).resolve().parent.parent
    sys.path.append(str(workspace_dir))
    from src.data_utils import load_config
    
    config_path = workspace_dir / "config" / "training_config.json"
    model_path = workspace_dir / "artifacts" / "models" / "efficientnet_final.keras"
    test_dir = workspace_dir / "processed_data" / "test"
    
    output_dir = workspace_dir / "artifacts" / "plots" / "gradcam"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading config and model...")
    config = load_config(config_path)
    classes = config["classes"]
    img_size = tuple(config["image_size"])
    model = tf.keras.models.load_model(str(model_path))
    
    # We want 2 correct examples per class, and maybe a few incorrect examples total.
    target_correct = 2
    target_incorrect = 5
    
    found_correct = {c: 0 for c in classes}
    found_incorrect = 0
    
    print("Scanning test set to generate Grad-CAM visual reports...")
    
    for class_name in classes:
        class_dir = test_dir / class_name
        if not class_dir.exists():
            continue
            
        images = [f for f in os.listdir(class_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        # Shuffle for randomness
        np.random.seed(42)
        np.random.shuffle(images)
        
        for img_name in images:
            if found_correct[class_name] >= target_correct and found_incorrect >= target_incorrect:
                break # Move to next class, though incorrect might need more scanning
                
            img_path = class_dir / img_name
            
            # Predict
            img = tf.keras.preprocessing.image.load_img(img_path, target_size=img_size)
            img_array = tf.keras.preprocessing.image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            
            preds = model.predict(img_array, verbose=0)
            pred_idx = np.argmax(preds[0])
            pred_class = classes[pred_idx]
            confidence = preds[0][pred_idx]
            
            is_correct = (pred_class == class_name)
            
            if is_correct and found_correct[class_name] < target_correct:
                print(f"Generating Correct case for {class_name}...")
                heatmap = make_gradcam_heatmap(img_array, model, "efficientnetb3")
                out_name = f"Correct_{class_name}_{found_correct[class_name]+1}.png"
                generate_composite_image(img_path, heatmap, class_name, pred_class, confidence, output_dir / out_name, img_size)
                found_correct[class_name] += 1
                
            elif not is_correct and found_incorrect < target_incorrect:
                print(f"Generating Incorrect case (True: {class_name}, Pred: {pred_class})...")
                heatmap = make_gradcam_heatmap(img_array, model, "efficientnetb3")
                out_name = f"Incorrect_True_{class_name}_Pred_{pred_class}_{found_incorrect+1}.png"
                generate_composite_image(img_path, heatmap, class_name, pred_class, confidence, output_dir / out_name, img_size)
                found_incorrect += 1
                
    print(f"Finished generating Grad-CAM plots at {output_dir}")

if __name__ == "__main__":
    main()
