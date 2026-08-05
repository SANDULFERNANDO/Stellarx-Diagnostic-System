from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report


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

OUTPUT_DIR = (
    PROJECT_ROOT
    / "ml_outputs_new_run"
    / "prediction_analysis"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 16

CLASS_NAMES = [
    "Eczema",
    "Leishmaniasis",
    "Tinea",
]

VALID_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}

MAX_CORRECT_EXAMPLES = 12
MAX_INCORRECT_EXAMPLES = 12
MAX_TINEA_EXAMPLES = 12

RANDOM_SEED = 42


# ---------------------------------------------------------
# Validate required paths
# ---------------------------------------------------------

def validate_paths() -> None:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    if not TEST_DIR.exists():
        raise FileNotFoundError(
            f"Test dataset not found: {TEST_DIR}"
        )


# ---------------------------------------------------------
# Collect test files in TensorFlow class order
# ---------------------------------------------------------

def collect_test_files() -> list[Path]:
    file_paths = []

    for class_name in CLASS_NAMES:
        class_folder = TEST_DIR / class_name

        if not class_folder.exists():
            raise FileNotFoundError(
                f"Class folder not found: "
                f"{class_folder}"
            )

        class_files = sorted(
            [
                file_path
                for file_path in class_folder.iterdir()
                if (
                    file_path.is_file()
                    and file_path.suffix.lower()
                    in VALID_EXTENSIONS
                )
            ],
            key=lambda path: path.name.lower(),
        )

        file_paths.extend(
            class_files
        )

    return file_paths


# ---------------------------------------------------------
# Prediction gallery
# ---------------------------------------------------------

def create_prediction_gallery(
    selected_indices: np.ndarray,
    filename: str,
    title: str,
    test_file_paths: list[Path],
    true_indices: np.ndarray,
    predicted_indices: np.ndarray,
    prediction_confidences: np.ndarray,
) -> None:
    if len(selected_indices) == 0:
        print(
            f"No images available for: "
            f"{filename}"
        )
        return

    columns = 3
    rows = int(
        np.ceil(
            len(selected_indices)
            / columns
        )
    )

    figure, axes = plt.subplots(
        rows,
        columns,
        figsize=(12, 4 * rows),
    )

    axes = np.atleast_1d(
        axes
    ).reshape(-1)

    for axis in axes:
        axis.axis("off")

    for plot_index, sample_index in enumerate(
        selected_indices
    ):
        file_path = test_file_paths[
            sample_index
        ]

        image = tf.keras.utils.load_img(
            file_path,
            target_size=IMAGE_SIZE,
        )

        actual_name = CLASS_NAMES[
            true_indices[sample_index]
        ]

        predicted_name = CLASS_NAMES[
            predicted_indices[sample_index]
        ]

        confidence = (
            prediction_confidences[
                sample_index
            ]
            * 100
        )

        axes[plot_index].imshow(
            image
        )

        axes[plot_index].set_title(
            f"Actual: {actual_name}\n"
            f"Predicted: {predicted_name}\n"
            f"Confidence: {confidence:.2f}%"
        )

        axes[plot_index].axis("off")

    figure.suptitle(
        title,
        fontsize=16,
    )

    figure.tight_layout(
        rect=[0, 0, 1, 0.97]
    )

    figure.savefig(
        OUTPUT_DIR / filename,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)


# ---------------------------------------------------------
# Tinea gallery
# ---------------------------------------------------------

def create_tinea_gallery(
    selected_indices: np.ndarray,
    test_file_paths: list[Path],
    predicted_indices: np.ndarray,
    prediction_confidences: np.ndarray,
    predicted_probabilities: np.ndarray,
) -> None:
    if len(selected_indices) == 0:
        print(
            "No Tinea images were available."
        )
        return

    tinea_index = CLASS_NAMES.index(
        "Tinea"
    )

    columns = 3
    rows = int(
        np.ceil(
            len(selected_indices)
            / columns
        )
    )

    figure, axes = plt.subplots(
        rows,
        columns,
        figsize=(12, 4 * rows),
    )

    axes = np.atleast_1d(
        axes
    ).reshape(-1)

    for axis in axes:
        axis.axis("off")

    for plot_index, sample_index in enumerate(
        selected_indices
    ):
        file_path = test_file_paths[
            sample_index
        ]

        image = tf.keras.utils.load_img(
            file_path,
            target_size=IMAGE_SIZE,
        )

        predicted_name = CLASS_NAMES[
            predicted_indices[sample_index]
        ]

        confidence = (
            prediction_confidences[
                sample_index
            ]
            * 100
        )

        tinea_probability = (
            predicted_probabilities[
                sample_index,
                tinea_index,
            ]
            * 100
        )

        axes[plot_index].imshow(
            image
        )

        axes[plot_index].set_title(
            f"Predicted: {predicted_name}\n"
            f"Confidence: {confidence:.2f}%\n"
            f"Tinea probability: "
            f"{tinea_probability:.2f}%"
        )

        axes[plot_index].axis("off")

    figure.suptitle(
        "Tinea Test-Set Prediction Examples",
        fontsize=16,
    )

    figure.tight_layout(
        rect=[0, 0, 1, 0.97]
    )

    figure.savefig(
        OUTPUT_DIR
        / "tinea_predictions.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)


# ---------------------------------------------------------
# Main analysis
# ---------------------------------------------------------

def main() -> None:
    validate_paths()

    print(
        "StellarX new-run prediction analysis"
    )
    print("=" * 70)

    print(
        f"Model: {MODEL_PATH}"
    )

    print(
        f"Test dataset: {TEST_DIR}"
    )

    print(
        f"Output folder: {OUTPUT_DIR}"
    )

    # -----------------------------------------------------
    # Load model and test dataset
    # -----------------------------------------------------

    print("\nLoading model...")

    model = tf.keras.models.load_model(
        MODEL_PATH
    )

    print("Loading test dataset...")

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

    if test_dataset.class_names != CLASS_NAMES:
        raise ValueError(
            "Class order mismatch.\n"
            f"Expected: {CLASS_NAMES}\n"
            f"Found: {test_dataset.class_names}"
        )

    test_file_paths = collect_test_files()

    # -----------------------------------------------------
    # Generate predictions
    # -----------------------------------------------------

    print("Generating predictions...")

    true_one_hot_batches = []
    probability_batches = []

    for image_batch, label_batch in test_dataset:
        batch_probabilities = model.predict(
            image_batch,
            verbose=0,
        )

        probability_batches.append(
            batch_probabilities
        )

        true_one_hot_batches.append(
            label_batch.numpy()
        )

    true_one_hot = np.concatenate(
        true_one_hot_batches,
        axis=0,
    )

    predicted_probabilities = np.concatenate(
        probability_batches,
        axis=0,
    )

    true_indices = np.argmax(
        true_one_hot,
        axis=1,
    )

    predicted_indices = np.argmax(
        predicted_probabilities,
        axis=1,
    )

    prediction_confidences = np.max(
        predicted_probabilities,
        axis=1,
    )

    correct_mask = (
        true_indices
        == predicted_indices
    )

    if len(test_file_paths) != len(
        true_indices
    ):
        raise ValueError(
            "Test file count does not match "
            "prediction count.\n"
            f"Files: {len(test_file_paths)}\n"
            f"Predictions: {len(true_indices)}"
        )

    # -----------------------------------------------------
    # Classification report and per-class chart
    # -----------------------------------------------------

    report = classification_report(
        true_indices,
        predicted_indices,
        target_names=CLASS_NAMES,
        output_dict=True,
        zero_division=0,
    )

    metrics = [
        "precision",
        "recall",
        "f1-score",
    ]

    x_positions = np.arange(
        len(CLASS_NAMES)
    )

    bar_width = 0.24

    figure, axis = plt.subplots(
        figsize=(10, 6)
    )

    for metric_index, metric_name in enumerate(
        metrics
    ):
        metric_values = [
            report[class_name][metric_name]
            for class_name in CLASS_NAMES
        ]

        positions = (
            x_positions
            + metric_index * bar_width
        )

        bars = axis.bar(
            positions,
            metric_values,
            width=bar_width,
            label=(
                metric_name
                .replace("-", " ")
                .title()
            ),
        )

        axis.bar_label(
            bars,
            labels=[
                f"{value:.3f}"
                for value in metric_values
            ],
            padding=3,
            fontsize=9,
        )

    axis.set_title(
        "Per-Class Classification Metrics"
    )

    axis.set_xlabel(
        "Skin lesion class"
    )

    axis.set_ylabel(
        "Score"
    )

    axis.set_ylim(
        0,
        1.10,
    )

    axis.set_xticks(
        x_positions + bar_width
    )

    axis.set_xticklabels(
        CLASS_NAMES
    )

    axis.legend()

    axis.grid(
        axis="y",
        alpha=0.25,
    )

    figure.tight_layout()

    figure.savefig(
        OUTPUT_DIR
        / "per_class_metrics.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)

    # -----------------------------------------------------
    # Confidence distribution
    # -----------------------------------------------------

    correct_confidences = (
        prediction_confidences[
            correct_mask
        ]
    )

    incorrect_confidences = (
        prediction_confidences[
            ~correct_mask
        ]
    )

    figure, axis = plt.subplots(
        figsize=(9, 6)
    )

    bins = np.linspace(
        0,
        1,
        21,
    )

    axis.hist(
        correct_confidences,
        bins=bins,
        alpha=0.70,
        label=(
            "Correct predictions "
            f"({len(correct_confidences)})"
        ),
    )

    if len(incorrect_confidences) > 0:
        axis.hist(
            incorrect_confidences,
            bins=bins,
            alpha=0.70,
            label=(
                "Incorrect predictions "
                f"({len(incorrect_confidences)})"
            ),
        )

    axis.set_title(
        "Prediction Confidence Distribution"
    )

    axis.set_xlabel(
        "Maximum predicted probability"
    )

    axis.set_ylabel(
        "Number of test images"
    )

    axis.legend()

    axis.grid(
        axis="y",
        alpha=0.25,
    )

    figure.tight_layout()

    figure.savefig(
        OUTPUT_DIR
        / "confidence_distribution.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)

    # -----------------------------------------------------
    # Select correct and incorrect examples
    # -----------------------------------------------------

    correct_indices = np.where(
        correct_mask
    )[0]

    incorrect_indices = np.where(
        ~correct_mask
    )[0]

    random_generator = np.random.default_rng(
        RANDOM_SEED
    )

    if len(correct_indices) > (
        MAX_CORRECT_EXAMPLES
    ):
        selected_correct_indices = (
            random_generator.choice(
                correct_indices,
                size=MAX_CORRECT_EXAMPLES,
                replace=False,
            )
        )
    else:
        selected_correct_indices = (
            correct_indices
        )

    # Sort incorrect predictions by confidence,
    # highest-confidence mistakes first.
    selected_incorrect_indices = (
        incorrect_indices[
            np.argsort(
                prediction_confidences[
                    incorrect_indices
                ]
            )[::-1]
        ][:MAX_INCORRECT_EXAMPLES]
    )

    create_prediction_gallery(
        selected_indices=(
            selected_correct_indices
        ),
        filename=(
            "correct_predictions.png"
        ),
        title="Correct Test Predictions",
        test_file_paths=test_file_paths,
        true_indices=true_indices,
        predicted_indices=predicted_indices,
        prediction_confidences=(
            prediction_confidences
        ),
    )

    create_prediction_gallery(
        selected_indices=(
            selected_incorrect_indices
        ),
        filename=(
            "incorrect_predictions.png"
        ),
        title=(
            "Incorrect Test Predictions"
        ),
        test_file_paths=test_file_paths,
        true_indices=true_indices,
        predicted_indices=predicted_indices,
        prediction_confidences=(
            prediction_confidences
        ),
    )

    # -----------------------------------------------------
    # Tinea analysis
    # -----------------------------------------------------

    tinea_index = CLASS_NAMES.index(
        "Tinea"
    )

    tinea_sample_indices = np.where(
        true_indices == tinea_index
    )[0]

    # Select a manageable set of Tinea examples:
    # six correct and up to six incorrect.
    tinea_correct_indices = (
        tinea_sample_indices[
            correct_mask[
                tinea_sample_indices
            ]
        ]
    )

    tinea_incorrect_indices = (
        tinea_sample_indices[
            ~correct_mask[
                tinea_sample_indices
            ]
        ]
    )

    selected_tinea_correct = (
        tinea_correct_indices[
            :6
        ]
    )

    selected_tinea_incorrect = (
        tinea_incorrect_indices[
            :6
        ]
    )

    selected_tinea_indices = np.concatenate(
        [
            selected_tinea_correct,
            selected_tinea_incorrect,
        ]
    )[:MAX_TINEA_EXAMPLES]

    create_tinea_gallery(
        selected_indices=(
            selected_tinea_indices
        ),
        test_file_paths=test_file_paths,
        predicted_indices=predicted_indices,
        prediction_confidences=(
            prediction_confidences
        ),
        predicted_probabilities=(
            predicted_probabilities
        ),
    )

    # -----------------------------------------------------
    # Save prediction details
    # -----------------------------------------------------

    prediction_records = []

    for sample_index, file_path in enumerate(
        test_file_paths
    ):
        record = {
            "file": str(
                file_path.relative_to(
                    TEST_DIR
                )
            ),
            "actual_class": CLASS_NAMES[
                true_indices[sample_index]
            ],
            "predicted_class": CLASS_NAMES[
                predicted_indices[
                    sample_index
                ]
            ],
            "confidence": float(
                prediction_confidences[
                    sample_index
                ]
            ),
            "correct": bool(
                correct_mask[sample_index]
            ),
            "probabilities": {
                class_name: float(
                    predicted_probabilities[
                        sample_index,
                        class_index,
                    ]
                )
                for class_index, class_name
                in enumerate(CLASS_NAMES)
            },
        }

        prediction_records.append(
            record
        )

    with (
        OUTPUT_DIR
        / "prediction_details.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as output_file:
        json.dump(
            prediction_records,
            output_file,
            indent=4,
        )

    # -----------------------------------------------------
    # Save summary
    # -----------------------------------------------------

    summary = {
        "total_test_images": int(
            len(true_indices)
        ),
        "correct_predictions": int(
            len(correct_indices)
        ),
        "incorrect_predictions": int(
            len(incorrect_indices)
        ),
        "overall_accuracy": float(
            len(correct_indices)
            / len(true_indices)
        ),
        "tinea_test_images": int(
            len(tinea_sample_indices)
        ),
        "mean_correct_confidence": float(
            np.mean(correct_confidences)
        ),
        "mean_incorrect_confidence": (
            float(
                np.mean(
                    incorrect_confidences
                )
            )
            if len(
                incorrect_confidences
            ) > 0
            else None
        ),
    }

    with (
        OUTPUT_DIR
        / "prediction_summary.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as output_file:
        json.dump(
            summary,
            output_file,
            indent=4,
        )

    # -----------------------------------------------------
    # Final output
    # -----------------------------------------------------

    print(
        "\nPrediction analysis completed."
    )

    print(
        f"Correct predictions: "
        f"{len(correct_indices)}"
    )

    print(
        f"Incorrect predictions: "
        f"{len(incorrect_indices)}"
    )

    print(
        f"Tinea test images: "
        f"{len(tinea_sample_indices)}"
    )

    print(
        f"Results saved to: "
        f"{OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()