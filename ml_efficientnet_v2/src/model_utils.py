import os
import numpy as np
import tensorflow as tf
from sklearn.utils.class_weight import compute_class_weight

def calculate_class_weights(train_dir, class_names):
    """
    Calculates class weights based on the actual image counts in the training directory.
    This helps the model pay more attention to underrepresented classes (like Leishmaniasis).
    """
    print("Calculating class weights...")
    y_train = []
    
    # Iterate through classes and count images
    for idx, class_name in enumerate(class_names):
        class_path = os.path.join(train_dir, class_name)
        if os.path.exists(class_path):
            count = len([f for f in os.listdir(class_path) if os.path.isfile(os.path.join(class_path, f))])
            y_train.extend([idx] * count)
            
    if not y_train:
        raise ValueError("No training data found to calculate class weights.")
        
    classes_unique = np.unique(y_train)
    weights = compute_class_weight(class_weight='balanced', classes=classes_unique, y=y_train)
    
    class_weights_dict = {i: weight for i, weight in zip(classes_unique, weights)}
    print(f"Computed Class Weights: {class_weights_dict}")
    return class_weights_dict

def build_efficientnet_model(input_shape, num_classes, dropout_rate=0.2):
    """
    Builds the EfficientNetB3 model for 4-class classification.
    Initially, the backbone is entirely frozen.
    """
    print("Building EfficientNetB3 model...")
    # Load pretrained EfficientNetB3 without the top classification layer
    backbone = tf.keras.applications.EfficientNetB3(
        include_top=False,
        weights='imagenet',
        input_shape=input_shape
    )
    
    # Freeze the backbone for Stage 1 training
    backbone.trainable = False
    
    # Construct the new classification head
    inputs = tf.keras.Input(shape=input_shape)
    x = backbone(inputs, training=False) # training=False forces BatchNorm to inference mode
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(dropout_rate)(x)
    outputs = tf.keras.layers.Dense(num_classes, activation='softmax')(x)
    
    model = tf.keras.Model(inputs, outputs)
    return model

def unfreeze_for_finetuning(model, unfreeze_blocks=20):
    """
    Unfreezes the top layers of the EfficientNetB3 backbone for fine-tuning,
    while strictly keeping BatchNormalization layers frozen to prevent weight corruption.
    """
    print("Unfreezing layers for Stage 2 Fine-tuning...")
    
    # The backbone is the first layer after the Input layer in our functional model
    backbone = model.layers[1]
    backbone.trainable = True
    
    # Freeze all layers except the top 'unfreeze_blocks' layers
    for layer in backbone.layers[:-unfreeze_blocks]:
        layer.trainable = False
        
    # Ensure all BatchNormalization layers remain completely frozen
    # This is a critical best practice for transfer learning
    for layer in backbone.layers:
        if isinstance(layer, tf.keras.layers.BatchNormalization):
            layer.trainable = False
            
    return model
