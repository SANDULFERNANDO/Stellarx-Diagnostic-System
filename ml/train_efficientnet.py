from pathlib import Path
import json
import random

import numpy as np
import tensorflow as tf
from sklearn.utils.class_weight import compute_class_weight


# ---------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------

RANDOM_SEED = 42

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
tf.random.set_seed(RANDOM_SEED)


# ---------------------------------------------------------
# Paths for the new training run
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_ROOT = (
    PROJECT_ROOT
    / "processed_dataset_new_run"
)

TRAIN_DIR = DATASET_ROOT / "train"
VALIDATION_DIR = DATASET_ROOT / "validation"
TEST_DIR = DATASET_ROOT / "test"

OUTPUT_ROOT = (
    PROJECT_ROOT
    / "ml_outputs_new_run"
    / "training"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "models_new_run"
)

OUTPUT_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ---------------------------------------------------------
# Training configuration
# ---------------------------------------------------------

IMAGE_HEIGHT = 224
IMAGE_WIDTH = 224
IMAGE_SIZE = (
    IMAGE_HEIGHT,
    IMAGE_WIDTH,
)

BATCH_SIZE = 16

# Stage 1: train only the new classification head
FROZEN_EPOCHS = 15

# Stage 2: fine-tune upper EfficientNet layers
FINE_TUNE_EPOCHS = 15

INITIAL_LEARNING_RATE = 1e-4
FINE_TUNE_LEARNING_RATE = 1e-5

# EfficientNetB0 has approximately 237 layers.
# Layers before this index remain frozen.
FINE_TUNE_FROM_LAYER = 200

DROPOUT_RATE = 0.30

AUTOTUNE = tf.data.AUTOTUNE

VALID_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


# ---------------------------------------------------------
# Validate required dataset folders
# ---------------------------------------------------------

def validate_dataset_structure() -> None:
    required_directories = [
        TRAIN_DIR,
        VALIDATION_DIR,
        TEST_DIR,
    ]

    for directory in required_directories:
        if not directory.exists():
            raise FileNotFoundError(
                f"Required dataset directory was not found: "
                f"{directory}"
            )

    expected_classes = {
        "Eczema",
        "Leishmaniasis",
        "Tinea",
    }

    for split_directory in required_directories:
        available_classes = {
            folder.name
            for folder in split_directory.iterdir()
            if folder.is_dir()
        }

        if available_classes != expected_classes:
            raise ValueError(
                f"Unexpected classes in {split_directory}.\n"
                f"Expected: {sorted(expected_classes)}\n"
                f"Found: {sorted(available_classes)}"
            )


# ---------------------------------------------------------
# Count images in one class folder
# ---------------------------------------------------------

def count_images(
    class_directory: Path,
) -> int:
    return sum(
        1
        for file_path in class_directory.iterdir()
        if (
            file_path.is_file()
            and file_path.suffix.lower()
            in VALID_IMAGE_EXTENSIONS
        )
    )


# ---------------------------------------------------------
# Save history as JSON
# ---------------------------------------------------------

def save_history(
    history: tf.keras.callbacks.History,
    output_path: Path,
) -> None:
    history_data = {
        metric_name: [
            float(value)
            for value in values
        ]
        for metric_name, values
        in history.history.items()
    }

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as history_file:
        json.dump(
            history_data,
            history_file,
            indent=4,
        )


# ---------------------------------------------------------
# Main training function
# ---------------------------------------------------------

def main() -> None:
    validate_dataset_structure()

    print("StellarX EfficientNetB0 new training run")
    print("=" * 70)

    print(
        f"TensorFlow version: "
        f"{tf.__version__}"
    )

    print(
        f"Project root: "
        f"{PROJECT_ROOT}"
    )

    print(
        f"Dataset root: "
        f"{DATASET_ROOT}"
    )

    print(
        f"Model output folder: "
        f"{MODEL_DIR}"
    )

    print(
        f"Training output folder: "
        f"{OUTPUT_ROOT}"
    )

    physical_gpus = (
        tf.config.list_physical_devices("GPU")
    )

    if physical_gpus:
        print(
            f"GPU detected: "
            f"{physical_gpus}"
        )
    else:
        print(
            "No GPU detected. "
            "Training will use CPU."
        )

    # -----------------------------------------------------
    # Load datasets
    # -----------------------------------------------------

    train_dataset = (
        tf.keras.utils.image_dataset_from_directory(
            TRAIN_DIR,
            labels="inferred",
            label_mode="categorical",
            image_size=IMAGE_SIZE,
            batch_size=BATCH_SIZE,
            shuffle=True,
            seed=RANDOM_SEED,
        )
    )

    validation_dataset = (
        tf.keras.utils.image_dataset_from_directory(
            VALIDATION_DIR,
            labels="inferred",
            label_mode="categorical",
            image_size=IMAGE_SIZE,
            batch_size=BATCH_SIZE,
            shuffle=False,
        )
    )

    test_dataset = (
        tf.keras.utils.image_dataset_from_directory(
            TEST_DIR,
            labels="inferred",
            label_mode="categorical",
            image_size=IMAGE_SIZE,
            batch_size=BATCH_SIZE,
            shuffle=False,
        )
    )

    class_names = train_dataset.class_names
    number_of_classes = len(class_names)

    print("\nClass names:")
    print(class_names)

    if class_names != [
        "Eczema",
        "Leishmaniasis",
        "Tinea",
    ]:
        raise ValueError(
            "Unexpected TensorFlow class order. "
            f"Found: {class_names}"
        )

    with (
        OUTPUT_ROOT
        / "class_names.txt"
    ).open(
        "w",
        encoding="utf-8",
    ) as class_file:
        for class_name in class_names:
            class_file.write(
                f"{class_name}\n"
            )

    # -----------------------------------------------------
    # Display dataset counts
    # -----------------------------------------------------

    dataset_counts = {
        "train": {},
        "validation": {},
        "test": {},
    }

    split_directories = {
        "train": TRAIN_DIR,
        "validation": VALIDATION_DIR,
        "test": TEST_DIR,
    }

    print("\nDataset counts")
    print("=" * 70)

    for split_name, split_directory in (
        split_directories.items()
    ):
        split_total = 0

        for class_name in class_names:
            image_count = count_images(
                split_directory / class_name
            )

            dataset_counts[
                split_name
            ][class_name] = image_count

            split_total += image_count

            print(
                f"{split_name} / "
                f"{class_name}: "
                f"{image_count}"
            )

        dataset_counts[
            split_name
        ]["total"] = split_total

        print(
            f"{split_name} total: "
            f"{split_total}"
        )

    with (
        OUTPUT_ROOT
        / "dataset_counts.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as count_file:
        json.dump(
            dataset_counts,
            count_file,
            indent=4,
        )

    # -----------------------------------------------------
    # Improve pipeline performance
    # -----------------------------------------------------

    train_dataset = train_dataset.prefetch(
        buffer_size=AUTOTUNE
    )

    validation_dataset = (
        validation_dataset.prefetch(
            buffer_size=AUTOTUNE
        )
    )

    test_dataset = test_dataset.prefetch(
        buffer_size=AUTOTUNE
    )

    # -----------------------------------------------------
    # Calculate class weights from training data
    # -----------------------------------------------------

    training_labels = []

    for class_index, class_name in enumerate(
        class_names
    ):
        class_directory = (
            TRAIN_DIR
            / class_name
        )

        image_count = count_images(
            class_directory
        )

        training_labels.extend(
            [class_index] * image_count
        )

    training_labels = np.array(
        training_labels
    )

    calculated_weights = compute_class_weight(
        class_weight="balanced",
        classes=np.arange(
            number_of_classes
        ),
        y=training_labels,
    )

    class_weights = {
        class_index: float(weight)
        for class_index, weight
        in enumerate(calculated_weights)
    }

    print("\nClass weights")
    print("=" * 70)

    for class_index, class_name in enumerate(
        class_names
    ):
        print(
            f"{class_index} - "
            f"{class_name}: "
            f"{class_weights[class_index]:.4f}"
        )

    with (
        OUTPUT_ROOT
        / "class_weights.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as weight_file:
        json.dump(
            {
                class_names[class_index]: weight
                for class_index, weight
                in class_weights.items()
            },
            weight_file,
            indent=4,
        )

    # -----------------------------------------------------
    # Data augmentation
    # Only active during model.fit()
    # -----------------------------------------------------

    data_augmentation = tf.keras.Sequential(
        [
            tf.keras.layers.RandomFlip(
                mode="horizontal",
                seed=RANDOM_SEED,
            ),
            tf.keras.layers.RandomRotation(
                factor=0.08,
                seed=RANDOM_SEED,
            ),
            tf.keras.layers.RandomZoom(
                height_factor=0.10,
                width_factor=0.10,
                seed=RANDOM_SEED,
            ),
            tf.keras.layers.RandomTranslation(
                height_factor=0.05,
                width_factor=0.05,
                seed=RANDOM_SEED,
            ),
            tf.keras.layers.RandomContrast(
                factor=0.10,
                seed=RANDOM_SEED,
            ),
        ],
        name="data_augmentation",
    )

    # -----------------------------------------------------
    # Build EfficientNetB0
    # -----------------------------------------------------

    print(
        "\nLoading ImageNet-pretrained "
        "EfficientNetB0..."
    )

    base_model = (
        tf.keras.applications.EfficientNetB0(
            weights="imagenet",
            include_top=False,
            input_shape=(
                IMAGE_HEIGHT,
                IMAGE_WIDTH,
                3,
            ),
        )
    )

    base_model.trainable = False

    input_layer = tf.keras.Input(
        shape=(
            IMAGE_HEIGHT,
            IMAGE_WIDTH,
            3,
        ),
        name="input_image",
    )

    x = data_augmentation(
        input_layer
    )

    # EfficientNetB0 includes its own rescaling.
    # Input remains in the 0–255 range.
    x = base_model(
        x,
        training=False,
    )

    x = (
        tf.keras.layers.GlobalAveragePooling2D(
            name="global_average_pooling"
        )(x)
    )

    x = tf.keras.layers.Dropout(
        rate=DROPOUT_RATE,
        name="dropout",
    )(x)

    output_layer = tf.keras.layers.Dense(
        units=number_of_classes,
        activation="softmax",
        name="predictions",
    )(x)

    model = tf.keras.Model(
        inputs=input_layer,
        outputs=output_layer,
        name="StellarX_EfficientNetB0_New_Run",
    )

    # -----------------------------------------------------
    # Save training configuration
    # -----------------------------------------------------

    training_configuration = {
        "random_seed": RANDOM_SEED,
        "image_size": [
            IMAGE_HEIGHT,
            IMAGE_WIDTH,
        ],
        "batch_size": BATCH_SIZE,
        "frozen_epochs": FROZEN_EPOCHS,
        "fine_tune_epochs": FINE_TUNE_EPOCHS,
        "initial_learning_rate": (
            INITIAL_LEARNING_RATE
        ),
        "fine_tune_learning_rate": (
            FINE_TUNE_LEARNING_RATE
        ),
        "fine_tune_from_layer": (
            FINE_TUNE_FROM_LAYER
        ),
        "dropout_rate": DROPOUT_RATE,
        "class_names": class_names,
    }

    with (
        OUTPUT_ROOT
        / "training_configuration.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as configuration_file:
        json.dump(
            training_configuration,
            configuration_file,
            indent=4,
        )

    # -----------------------------------------------------
    # Stage 1: Frozen-base training
    # -----------------------------------------------------

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=(
                INITIAL_LEARNING_RATE
            )
        ),
        loss="categorical_crossentropy",
        metrics=[
            tf.keras.metrics.CategoricalAccuracy(
                name="accuracy"
            ),
            tf.keras.metrics.Precision(
                name="precision"
            ),
            tf.keras.metrics.Recall(
                name="recall"
            ),
        ],
    )

    print("\nModel summary")
    print("=" * 70)

    model.summary()

    frozen_checkpoint = (
        MODEL_DIR
        / "efficientnetb0_new_frozen_best.keras"
    )

    frozen_callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=frozen_checkpoint,
            monitor="val_accuracy",
            save_best_only=True,
            mode="max",
            verbose=1,
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=5,
            restore_best_weights=True,
            verbose=1,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,
            min_lr=1e-7,
            verbose=1,
        ),
        tf.keras.callbacks.CSVLogger(
            filename=(
                OUTPUT_ROOT
                / "frozen_training_log.csv"
            ),
            append=False,
        ),
        tf.keras.callbacks.TerminateOnNaN(),
    ]

    print("\nStage 1: Frozen-base training")
    print("=" * 70)

    frozen_history = model.fit(
        train_dataset,
        validation_data=validation_dataset,
        epochs=FROZEN_EPOCHS,
        class_weight=class_weights,
        callbacks=frozen_callbacks,
    )

    save_history(
        history=frozen_history,
        output_path=(
            OUTPUT_ROOT
            / "frozen_history.json"
        ),
    )

    # -----------------------------------------------------
    # Stage 2: Fine-tuning
    # -----------------------------------------------------

    base_model.trainable = True

    for layer_index, layer in enumerate(
        base_model.layers
    ):
        if layer_index < FINE_TUNE_FROM_LAYER:
            layer.trainable = False
        else:
            layer.trainable = True

        # Batch-normalization layers remain frozen
        # to protect pretrained statistics.
        if isinstance(
            layer,
            tf.keras.layers.BatchNormalization,
        ):
            layer.trainable = False

    trainable_layers = sum(
        1
        for layer in base_model.layers
        if layer.trainable
    )

    frozen_layers = sum(
        1
        for layer in base_model.layers
        if not layer.trainable
    )

    print("\nFine-tuning configuration")
    print("=" * 70)

    print(
        f"Total EfficientNet layers: "
        f"{len(base_model.layers)}"
    )

    print(
        f"Fine-tuning begins from layer: "
        f"{FINE_TUNE_FROM_LAYER}"
    )

    print(
        f"Trainable base-model layers: "
        f"{trainable_layers}"
    )

    print(
        f"Frozen base-model layers: "
        f"{frozen_layers}"
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=(
                FINE_TUNE_LEARNING_RATE
            )
        ),
        loss="categorical_crossentropy",
        metrics=[
            tf.keras.metrics.CategoricalAccuracy(
                name="accuracy"
            ),
            tf.keras.metrics.Precision(
                name="precision"
            ),
            tf.keras.metrics.Recall(
                name="recall"
            ),
        ],
    )

    fine_tuned_checkpoint = (
        MODEL_DIR
        / "efficientnetb0_new_finetuned_best.keras"
    )

    fine_tune_callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=fine_tuned_checkpoint,
            monitor="val_accuracy",
            save_best_only=True,
            mode="max",
            verbose=1,
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=5,
            restore_best_weights=True,
            verbose=1,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,
            min_lr=1e-7,
            verbose=1,
        ),
        tf.keras.callbacks.CSVLogger(
            filename=(
                OUTPUT_ROOT
                / "fine_tuning_log.csv"
            ),
            append=False,
        ),
        tf.keras.callbacks.TerminateOnNaN(),
    ]

    print("\nStage 2: Fine-tuning")
    print("=" * 70)

    fine_tune_history = model.fit(
        train_dataset,
        validation_data=validation_dataset,
        epochs=FINE_TUNE_EPOCHS,
        class_weight=class_weights,
        callbacks=fine_tune_callbacks,
    )

    save_history(
        history=fine_tune_history,
        output_path=(
            OUTPUT_ROOT
            / "fine_tune_history.json"
        ),
    )

    # -----------------------------------------------------
    # Save final fine-tuned model
    # -----------------------------------------------------

    final_model_path = (
        MODEL_DIR
        / "stellarx_efficientnetb0_new_final.keras"
    )

    model.save(
        final_model_path
    )

    # -----------------------------------------------------
    # Initial test evaluation
    # -----------------------------------------------------

    print("\nFinal test evaluation")
    print("=" * 70)

    test_results = model.evaluate(
        test_dataset,
        verbose=1,
        return_dict=True,
    )

    print("\nTest metrics")

    for metric_name, metric_value in (
        test_results.items()
    ):
        print(
            f"{metric_name}: "
            f"{metric_value:.4f}"
        )

    with (
        OUTPUT_ROOT
        / "test_metrics.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as metric_file:
        json.dump(
            {
                metric_name: float(
                    metric_value
                )
                for metric_name, metric_value
                in test_results.items()
            },
            metric_file,
            indent=4,
        )

    print(
        "\nTraining completed successfully."
    )

    print(
        f"Final model saved to: "
        f"{final_model_path}"
    )

    print(
        f"Best frozen model: "
        f"{frozen_checkpoint}"
    )

    print(
        f"Best fine-tuned model: "
        f"{fine_tuned_checkpoint}"
    )

    print(
        f"Training outputs: "
        f"{OUTPUT_ROOT}"
    )


if __name__ == "__main__":
    main()