import json
from pathlib import Path
import tensorflow as tf

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def build_augmentation_layer(config):
    """
    Builds a Keras sequential model for data augmentation.
    This will be applied ONLY to the training dataset.
    """
    aug_config = config.get("augmentation", {})
    layers = []
    
    if "random_flip" in aug_config:
        layers.append(tf.keras.layers.RandomFlip(aug_config["random_flip"]))
        
    if "random_rotation" in aug_config:
        layers.append(tf.keras.layers.RandomRotation(aug_config["random_rotation"]))
        
    if "random_zoom" in aug_config:
        layers.append(tf.keras.layers.RandomZoom(aug_config["random_zoom"]))
        
    return tf.keras.Sequential(layers, name="data_augmentation")

def create_dataset(data_dir, config, split_name, augment=False):
    """
    Creates a tf.data.Dataset from a directory.
    
    Args:
        data_dir: Path to the specific split (e.g., 'processed_data/train')
        config: Loaded config dictionary
        split_name: Name of split (for logging purposes)
        augment: Whether to apply data augmentation (True for train, False for val/test)
    """
    img_size = tuple(config["image_size"])
    batch_size = config["batch_size"]
    seed = config["seed"]
    
    # 1. Load images from directory
    # image_dataset_from_directory handles decoding, resizing, and converting to RGB
    ds = tf.keras.utils.image_dataset_from_directory(
        directory=data_dir,
        labels="inferred",
        label_mode="categorical",
        class_names=config["classes"],
        color_mode="rgb",
        batch_size=batch_size,
        image_size=img_size,
        shuffle=(split_name == 'train'), # Only shuffle training data
        seed=seed if split_name == 'train' else None,
        interpolation="bilinear"
    )
    
    # 2. Apply augmentation (Training only)
    if augment:
        data_augmentation = build_augmentation_layer(config)
        # Apply augmentation to images, keep labels intact
        ds = ds.map(lambda x, y: (data_augmentation(x, training=True), y),
                    num_parallel_calls=tf.data.AUTOTUNE)
    
    # Note: We do NOT apply Rescaling(1./255) here because EfficientNetB0 in Keras 
    # expects inputs in [0, 255] and has a built-in Normalization layer at the start 
    # of the model architecture.
    
    # 3. Performance optimization
    ds = ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    
    return ds

def load_all_datasets(processed_data_dir, config_path):
    """
    Loads train, val, and test datasets.
    """
    config = load_config(config_path)
    data_root = Path(processed_data_dir)
    
    train_ds = create_dataset(data_root / "train", config, "train", augment=True)
    val_ds = create_dataset(data_root / "val", config, "val", augment=False)
    test_ds = create_dataset(data_root / "test", config, "test", augment=False)
    
    return train_ds, val_ds, test_ds, config
