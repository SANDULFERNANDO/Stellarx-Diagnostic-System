from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from PIL import Image


# ---------------------------------------------------------
# Paths and configuration
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

TEST_DIR = (
    PROJECT_ROOT
    / "processed_dataset_new_run"
    / "test"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "models_new_run"
    / "stellarx_efficientnetb0_new_final.keras"
)

PREDICTION_DETAILS_PATH = (
    PROJECT_ROOT
    / "ml_outputs_new_run"
    / "prediction_analysis"
    / "prediction_details.json"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "ml_outputs_new_run"
    / "gradcam"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

IMAGE_SIZE = (224, 224)

CLASS_NAMES = [
    "Eczema",
    "Leishmaniasis",
    "Tinea",
]

MAX_CORRECT_EXAMPLES = 6
MAX_INCORRECT_EXAMPLES = 9


# ---------------------------------------------------------
# Validate required files
# ---------------------------------------------------------

def validate_required_files() -> None:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    if not TEST_DIR.exists():
        raise FileNotFoundError(
            f"Test dataset not found: {TEST_DIR}"
        )

    if not PREDICTION_DETAILS_PATH.exists():
        raise FileNotFoundError(
            "Prediction details were not found. "
            "Run analyze_predictions.py first."
        )


# ---------------------------------------------------------
# Load image
# ---------------------------------------------------------

def load_image_tensor(
    image_path: Path,
) -> tuple[Image.Image, tf.Tensor]:
    image = tf.keras.utils.load_img(
        image_path,
        target_size=IMAGE_SIZE,
    )

    image_array = tf.keras.utils.img_to_array(
        image
    )

    image_batch = tf.expand_dims(
        image_array,
        axis=0,
    )

    image_batch = tf.cast(
        image_batch,
        tf.float32,
    )

    return image, image_batch


# ---------------------------------------------------------
# Generate Grad-CAM heatmap
# ---------------------------------------------------------

def generate_gradcam_heatmap(
    image_batch: tf.Tensor,
    predicted_class_index: int,
    augmentation_layer: tf.keras.layers.Layer,
    feature_extractor: tf.keras.Model,
    pooling_layer: tf.keras.layers.Layer,
    dropout_layer: tf.keras.layers.Layer,
    prediction_layer: tf.keras.layers.Layer,
) -> np.ndarray:
    with tf.GradientTape() as tape:
        augmented_images = augmentation_layer(
            image_batch,
            training=False,
        )

        feature_maps = feature_extractor(
            augmented_images,
            training=False,
        )

        tape.watch(feature_maps)

        pooled_features = pooling_layer(
            feature_maps
        )

        dropped_features = dropout_layer(
            pooled_features,
            training=False,
        )

        predictions = prediction_layer(
            dropped_features
        )

        class_score = predictions[
            :,
            predicted_class_index,
        ]

    gradients = tape.gradient(
        class_score,
        feature_maps,
    )

    if gradients is None:
        raise ValueError(
            "Gradients could not be calculated "
            "for the selected image."
        )

    pooled_gradients = tf.reduce_mean(
        gradients,
        axis=(0, 1, 2),
    )

    feature_maps = feature_maps[0]

    heatmap = tf.reduce_sum(
        feature_maps * pooled_gradients,
        axis=-1,
    )

    heatmap = tf.maximum(
        heatmap,
        0,
    )

    maximum_value = tf.reduce_max(
        heatmap
    )

    if float(maximum_value.numpy()) > 0:
        heatmap = heatmap / maximum_value

    return heatmap.numpy()


# ---------------------------------------------------------
# Create Grad-CAM overlay
# ---------------------------------------------------------

def create_overlay(
    original_image: Image.Image,
    heatmap: np.ndarray,
    alpha: float = 0.40,
) -> np.ndarray:
    heatmap_uint8 = np.uint8(
        255 * heatmap
    )

    color_map = plt.get_cmap(
        "jet"
    )

    color_values = color_map(
        np.arange(256)
    )[:, :3]

    colored_heatmap = color_values[
        heatmap_uint8
    ]

    colored_heatmap = Image.fromarray(
        np.uint8(
            colored_heatmap * 255
        )
    )

    colored_heatmap = colored_heatmap.resize(
        original_image.size,
        Image.Resampling.BILINEAR,
    )

    colored_heatmap_array = np.array(
        colored_heatmap
    ).astype(
        np.float32
    )

    original_array = np.array(
        original_image.convert("RGB")
    ).astype(
        np.float32
    )

    overlay = (
        original_array * (1 - alpha)
        + colored_heatmap_array * alpha
    )

    return np.clip(
        overlay,
        0,
        255,
    ).astype(
        np.uint8
    )


# ---------------------------------------------------------
# Create Grad-CAM gallery
# ---------------------------------------------------------

def create_gradcam_gallery(
    records: list[dict],
    filename: str,
    title: str,
    augmentation_layer: tf.keras.layers.Layer,
    feature_extractor: tf.keras.Model,
    pooling_layer: tf.keras.layers.Layer,
    dropout_layer: tf.keras.layers.Layer,
    prediction_layer: tf.keras.layers.Layer,
) -> None:
    if not records:
        print(
            f"No records available for {filename}"
        )
        return

    rows = len(records)
    columns = 3

    figure, axes = plt.subplots(
        rows,
        columns,
        figsize=(12, 4 * rows),
    )

    if rows == 1:
        axes = np.expand_dims(
            axes,
            axis=0,
        )

    for row_index, record in enumerate(
        records
    ):
        image_path = (
            TEST_DIR
            / record["file"]
        )

        if not image_path.exists():
            print(
                f"Image not found: {image_path}"
            )
            continue

        original_image, image_batch = (
            load_image_tensor(
                image_path
            )
        )

        predicted_class = record[
            "predicted_class"
        ]

        predicted_class_index = (
            CLASS_NAMES.index(
                predicted_class
            )
        )

        heatmap = generate_gradcam_heatmap(
            image_batch=image_batch,
            predicted_class_index=(
                predicted_class_index
            ),
            augmentation_layer=(
                augmentation_layer
            ),
            feature_extractor=(
                feature_extractor
            ),
            pooling_layer=pooling_layer,
            dropout_layer=dropout_layer,
            prediction_layer=prediction_layer,
        )

        overlay = create_overlay(
            original_image,
            heatmap,
        )

        axes[row_index, 0].imshow(
            original_image
        )

        axes[row_index, 0].set_title(
            "Original image"
        )

        axes[row_index, 0].axis(
            "off"
        )

        axes[row_index, 1].imshow(
            heatmap,
            cmap="jet",
            vmin=0,
            vmax=1,
        )

        axes[row_index, 1].set_title(
            "Grad-CAM heatmap"
        )

        axes[row_index, 1].axis(
            "off"
        )

        axes[row_index, 2].imshow(
            overlay
        )

        axes[row_index, 2].set_title(
            f"Actual: {record['actual_class']}\n"
            f"Predicted: {predicted_class}\n"
            f"Confidence: "
            f"{record['confidence'] * 100:.2f}%"
        )

        axes[row_index, 2].axis(
            "off"
        )

    figure.suptitle(
        title,
        fontsize=16,
    )

    figure.tight_layout(
        rect=[0, 0, 1, 0.98]
    )

    output_file = (
        OUTPUT_DIR
        / filename
    )

    figure.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(
        figure
    )

    print(
        f"Saved: {output_file}"
    )


# ---------------------------------------------------------
# Main program
# ---------------------------------------------------------

def main() -> None:
    validate_required_files()

    print(
        "StellarX new-run Grad-CAM analysis"
    )
    print("=" * 70)

    print(
        f"Model: {MODEL_PATH}"
    )

    print(
        f"Test dataset: {TEST_DIR}"
    )

    print(
        f"Prediction details: "
        f"{PREDICTION_DETAILS_PATH}"
    )

    print(
        f"Output folder: {OUTPUT_DIR}"
    )

    # -----------------------------------------------------
    # Load model and prediction records
    # -----------------------------------------------------

    print("\nLoading trained model...")

    model = tf.keras.models.load_model(
        MODEL_PATH
    )

    with PREDICTION_DETAILS_PATH.open(
        "r",
        encoding="utf-8",
    ) as prediction_file:
        prediction_records = json.load(
            prediction_file
        )

    # -----------------------------------------------------
    # Find nested EfficientNet model
    # -----------------------------------------------------

    base_model = None

    for layer in model.layers:
        if (
            isinstance(layer, tf.keras.Model)
            and "efficientnet"
            in layer.name.lower()
        ):
            base_model = layer
            break

    if base_model is None:
        raise ValueError(
            "EfficientNetB0 base model could not "
            "be found inside the trained model."
        )

    # -----------------------------------------------------
    # Find final 4D feature layer
    # -----------------------------------------------------

    last_conv_layer = None

    for layer in reversed(
        base_model.layers
    ):
        try:
            output_shape = layer.output.shape
        except AttributeError:
            continue

        if len(output_shape) == 4:
            last_conv_layer = layer
            break

    if last_conv_layer is None:
        raise ValueError(
            "A suitable convolutional feature "
            "layer could not be found."
        )

    print(
        f"Base model: {base_model.name}"
    )

    print(
        f"Grad-CAM layer: "
        f"{last_conv_layer.name}"
    )

    # -----------------------------------------------------
    # Get outer model layers
    # -----------------------------------------------------

    augmentation_layer = model.get_layer(
        "data_augmentation"
    )

    pooling_layer = model.get_layer(
        "global_average_pooling"
    )

    dropout_layer = model.get_layer(
        "dropout"
    )

    prediction_layer = model.get_layer(
        "predictions"
    )

    feature_extractor = tf.keras.Model(
        inputs=base_model.input,
        outputs=last_conv_layer.output,
        name="efficientnet_feature_extractor",
    )

    # -----------------------------------------------------
    # Select examples
    # -----------------------------------------------------

    correct_records = [
        record
        for record in prediction_records
        if record["correct"]
    ]

    incorrect_records = [
        record
        for record in prediction_records
        if not record["correct"]
    ]

    selected_correct = []

    for class_name in CLASS_NAMES:
        class_records = [
            record
            for record in correct_records
            if (
                record["actual_class"]
                == class_name
            )
        ]

        # Use the two highest-confidence
        # correct examples from each class.
        class_records = sorted(
            class_records,
            key=lambda record: (
                record["confidence"]
            ),
            reverse=True,
        )

        selected_correct.extend(
            class_records[:2]
        )

    selected_correct = selected_correct[
        :MAX_CORRECT_EXAMPLES
    ]

    # Select the highest-confidence mistakes.
    # These are especially useful for error analysis.
    selected_incorrect = sorted(
        incorrect_records,
        key=lambda record: (
            record["confidence"]
        ),
        reverse=True,
    )[:MAX_INCORRECT_EXAMPLES]

    # -----------------------------------------------------
    # Generate galleries
    # -----------------------------------------------------

    create_gradcam_gallery(
        records=selected_correct,
        filename=(
            "correct_gradcam_examples.png"
        ),
        title=(
            "Grad-CAM Analysis of "
            "Correct Predictions"
        ),
        augmentation_layer=(
            augmentation_layer
        ),
        feature_extractor=(
            feature_extractor
        ),
        pooling_layer=pooling_layer,
        dropout_layer=dropout_layer,
        prediction_layer=prediction_layer,
    )

    create_gradcam_gallery(
        records=selected_incorrect,
        filename=(
            "incorrect_gradcam_examples.png"
        ),
        title=(
            "Grad-CAM Analysis of "
            "Incorrect Predictions"
        ),
        augmentation_layer=(
            augmentation_layer
        ),
        feature_extractor=(
            feature_extractor
        ),
        pooling_layer=pooling_layer,
        dropout_layer=dropout_layer,
        prediction_layer=prediction_layer,
    )

    # -----------------------------------------------------
    # Final summary
    # -----------------------------------------------------

    print(
        "\nGrad-CAM generation completed."
    )

    print(
        f"Correct examples analyzed: "
        f"{len(selected_correct)}"
    )

    print(
        f"Incorrect examples analyzed: "
        f"{len(selected_incorrect)}"
    )

    print(
        f"Results saved to: "
        f"{OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()