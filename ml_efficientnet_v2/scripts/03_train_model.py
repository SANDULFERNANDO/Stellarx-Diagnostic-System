import os
import sys
from pathlib import Path
import tensorflow as tf

# Add src to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.data_utils import load_all_datasets
from src.model_utils import calculate_class_weights, build_efficientnet_model, unfreeze_for_finetuning

def main():
    # 1. Setup paths
    workspace_dir = Path(__file__).resolve().parent.parent
    config_path = workspace_dir / "config" / "training_config.json"
    processed_data_dir = workspace_dir / "processed_data"
    
    # 2. Load Datasets and Config
    print("Loading data pipelines...")
    train_ds, val_ds, test_ds, config = load_all_datasets(processed_data_dir, config_path)
    
    # 3. Calculate Class Weights
    class_weights = calculate_class_weights(processed_data_dir / "train", config["classes"])
    
    # 4. Build Model
    input_shape = (*config["image_size"], 3)
    model = build_efficientnet_model(input_shape, len(config["classes"]))
    
    # Compile Stage 1
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=config["learning_rate_stage1"]),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # 5. Callbacks
    checkpoint_path = str(workspace_dir / "artifacts" / "checkpoints" / "best_model.keras")
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=checkpoint_path,
            save_best_only=True,
            monitor='val_loss',
            mode='min',
            verbose=1
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.2,
            patience=3,
            min_lr=1e-6,
            verbose=1
        ),
        tf.keras.callbacks.CSVLogger(
            filename=str(workspace_dir / "artifacts" / "metrics" / "training_history.csv"),
            append=True
        )
    ]
    
    # 6. STAGE 1: Train Frozen Backbone
    print("\n--- Starting STAGE 1: Training Classification Head ---")
    history_stage1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=config["epochs_stage1"],
        class_weight=class_weights,
        callbacks=callbacks
    )
    
    # 7. STAGE 2: Fine-Tuning
    print("\n--- Starting STAGE 2: Fine-Tuning Backbone ---")
    model = unfreeze_for_finetuning(model, unfreeze_blocks=20)
    
    # Recompile with a much smaller learning rate
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=config["learning_rate_stage2"]),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    history_stage2 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=config["epochs_stage2"],
        class_weight=class_weights,
        callbacks=callbacks
    )
    
    # 8. Save Final Model
    final_model_path = str(workspace_dir / "artifacts" / "models" / "efficientnet_final.keras")
    model.save(final_model_path)
    print(f"\nTraining Complete. Final model saved to {final_model_path}")

if __name__ == "__main__":
    main()
