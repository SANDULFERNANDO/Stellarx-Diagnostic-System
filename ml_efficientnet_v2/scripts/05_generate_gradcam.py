import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pathlib import Path
import os
import sys

# Add src to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.data_utils import load_config

def get_img_array(img_path, size):
    img = tf.keras.utils.load_img(img_path, target_size=size)
    array = tf.keras.utils.img_to_array(img)
    array = np.expand_dims(array, axis=0)
    return array

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

def save_and_display_gradcam(img_path, heatmap, output_path, alpha=0.4):
    # Load the original image
    img = tf.keras.utils.load_img(img_path)
    img = tf.keras.utils.img_to_array(img)

    # Rescale heatmap to a range 0-255
    heatmap = np.uint8(255 * heatmap)

    # Use jet colormap to colorize heatmap
    jet = plt.get_cmap("jet")

    # Use RGB values of the colormap
    jet_colors = jet(np.arange(256))[:, :3]
    jet_heatmap = jet_colors[heatmap]

    # Create an image with RGB colorized heatmap
    jet_heatmap = tf.keras.utils.array_to_img(jet_heatmap)
    jet_heatmap = jet_heatmap.resize((img.shape[1], img.shape[0]))
    jet_heatmap = tf.keras.utils.img_to_array(jet_heatmap)

    # Superimpose the heatmap on original image
    superimposed_img = jet_heatmap * alpha + img
    superimposed_img = tf.keras.utils.array_to_img(superimposed_img)

    # Save the superimposed image
    superimposed_img.save(output_path)
    print(f"Saved Grad-CAM to {output_path}")

def main():
    workspace_dir = Path(__file__).resolve().parent.parent
    model_path = workspace_dir / "artifacts" / "models" / "efficientnet_final.keras"
    config_path = workspace_dir / "config" / "training_config.json"
    
    if not model_path.exists():
        print("Model not found. Please train the model first.")
        return
        
    config = load_config(config_path)
    model = tf.keras.models.load_model(str(model_path))
    
    # EfficientNetB3's last convolutional layer inside the backbone
    # We must extract the backbone model first since it's wrapped in our functional model
    backbone = model.layers[1] 
    last_conv_layer_name = "top_activation" # Specific to EfficientNetB3
    
    print("Grad-CAM utility is ready. You can import this script to generate visual explanations.")

if __name__ == "__main__":
    main()
