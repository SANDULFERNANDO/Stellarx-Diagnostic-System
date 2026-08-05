from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    auc,
    classification_report,
    confusion_matrix,
    precision_recall_curve,
    roc_curve,
)
from sklearn.preprocessing import label_binarize


# ---------------------------------------------------------
# Paths and settings
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

TRAINING_OUTPUT_DIR = (
    PROJECT_ROOT
    / "ml_outputs_new_run"
    / "training"
)

EVALUATION_OUTPUT_DIR = (
    PROJECT_ROOT
    / "ml_outputs_new_run"
    / "evaluation"
)

EVALUATION_OUTPUT_DIR.mkdir(
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


# ---------------------------------------------------------
# Validate required paths
# ---------------------------------------------------------

def validate_required_paths() -> None:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_PATH}"
        )

    if not TEST_DIR.exists():
        raise FileNotFoundError(
            f"Test dataset not found: {TEST_DIR}"
        )

    if not TRAINING_OUTPUT_DIR.exists():
        raise FileNotFoundError(
            f"Training output folder not found: "
            f"{TRAINING_OUTPUT_DIR}"
        )


# ---------------------------------------------------------
# Save JSON safely
# ---------------------------------------------------------

def save_json(
    output_path: Path,
    data: dict,
) -> None:
    with output_path.open(
        "w",
        encoding="utf-8",
    ) as output_file:
        json.dump(
            data,
            output_file,
            indent=4,
        )


# ---------------------------------------------------------
# Main evaluation
# ---------------------------------------------------------

def main() -> None:
    validate_required_paths()

    print("StellarX EfficientNetB0 new-run evaluation")
    print("=" * 70)

    print(f"Model path: {MODEL_PATH}")
    print(f"Test dataset: {TEST_DIR}")
    print(f"Evaluation output: {EVALUATION_OUTPUT_DIR}")

    # -----------------------------------------------------
    # Load final model and test dataset
    # -----------------------------------------------------

    print("\nLoading final model...")

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

    dataset_class_names = (
        test_dataset.class_names
    )

    print(
        f"Detected class order: "
        f"{dataset_class_names}"
    )

    if dataset_class_names != CLASS_NAMES:
        raise ValueError(
            "Class order mismatch.\n"
            f"Expected: {CLASS_NAMES}\n"
            f"Found: {dataset_class_names}"
        )

    test_dataset = test_dataset.prefetch(
        tf.data.AUTOTUNE
    )

    # -----------------------------------------------------
    # Generate predictions
    # -----------------------------------------------------

    print("\nGenerating predictions...")

    true_labels = []
    predicted_probabilities = []

    for image_batch, label_batch in test_dataset:
        batch_probabilities = model.predict(
            image_batch,
            verbose=0,
        )

        predicted_probabilities.append(
            batch_probabilities
        )

        true_labels.append(
            label_batch.numpy()
        )

    true_labels_one_hot = np.concatenate(
        true_labels,
        axis=0,
    )

    predicted_probabilities = np.concatenate(
        predicted_probabilities,
        axis=0,
    )

    true_class_indices = np.argmax(
        true_labels_one_hot,
        axis=1,
    )

    predicted_class_indices = np.argmax(
        predicted_probabilities,
        axis=1,
    )

    total_test_images = len(
        true_class_indices
    )

    print(
        f"Predictions generated for "
        f"{total_test_images} test images."
    )

    # -----------------------------------------------------
    # Classification report
    # -----------------------------------------------------

    report_text = classification_report(
        true_class_indices,
        predicted_class_indices,
        target_names=CLASS_NAMES,
        digits=4,
        zero_division=0,
    )

    print("\nClassification report")
    print("=" * 70)
    print(report_text)

    report_file = (
        EVALUATION_OUTPUT_DIR
        / "classification_report.txt"
    )

    report_file.write_text(
        report_text,
        encoding="utf-8",
    )

    report_dictionary = classification_report(
        true_class_indices,
        predicted_class_indices,
        target_names=CLASS_NAMES,
        output_dict=True,
        zero_division=0,
    )

    save_json(
        EVALUATION_OUTPUT_DIR
        / "classification_report.json",
        report_dictionary,
    )

    # -----------------------------------------------------
    # Confusion matrices
    # -----------------------------------------------------

    matrix = confusion_matrix(
        true_class_indices,
        predicted_class_indices,
        labels=np.arange(
            len(CLASS_NAMES)
        ),
    )

    print("\nConfusion matrix")
    print("=" * 70)
    print(matrix)

    save_json(
        EVALUATION_OUTPUT_DIR
        / "confusion_matrix_counts.json",
        {
            "class_names": CLASS_NAMES,
            "matrix": matrix.tolist(),
        },
    )

    count_figure, count_axis = plt.subplots(
        figsize=(8, 7)
    )

    count_display = ConfusionMatrixDisplay(
        confusion_matrix=matrix,
        display_labels=CLASS_NAMES,
    )

    count_display.plot(
        ax=count_axis,
        values_format="d",
        cmap="Blues",
        colorbar=False,
    )

    count_axis.set_title(
        "StellarX Confusion Matrix — Counts"
    )

    count_figure.tight_layout()

    count_figure.savefig(
        EVALUATION_OUTPUT_DIR
        / "confusion_matrix_counts.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(count_figure)

    row_totals = matrix.sum(
        axis=1,
        keepdims=True,
    )

    normalized_matrix = np.divide(
        matrix,
        row_totals,
        out=np.zeros_like(
            matrix,
            dtype=float,
        ),
        where=row_totals != 0,
    )

    save_json(
        EVALUATION_OUTPUT_DIR
        / "confusion_matrix_normalized.json",
        {
            "class_names": CLASS_NAMES,
            "matrix": (
                normalized_matrix.tolist()
            ),
        },
    )

    normalized_figure, normalized_axis = (
        plt.subplots(
            figsize=(8, 7)
        )
    )

    normalized_display = ConfusionMatrixDisplay(
        confusion_matrix=normalized_matrix,
        display_labels=CLASS_NAMES,
    )

    normalized_display.plot(
        ax=normalized_axis,
        values_format=".2%",
        cmap="Blues",
        colorbar=False,
    )

    normalized_axis.set_title(
        "StellarX Confusion Matrix — Normalized"
    )

    normalized_figure.tight_layout()

    normalized_figure.savefig(
        EVALUATION_OUTPUT_DIR
        / "confusion_matrix_normalized.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(normalized_figure)

    # -----------------------------------------------------
    # ROC curves
    # -----------------------------------------------------

    binarized_true_labels = label_binarize(
        true_class_indices,
        classes=np.arange(
            len(CLASS_NAMES)
        ),
    )

    roc_figure, roc_axis = plt.subplots(
        figsize=(9, 7)
    )

    roc_auc_values = {}

    for class_index, class_name in enumerate(
        CLASS_NAMES
    ):
        (
            false_positive_rate,
            true_positive_rate,
            _,
        ) = roc_curve(
            binarized_true_labels[
                :,
                class_index,
            ],
            predicted_probabilities[
                :,
                class_index,
            ],
        )

        class_auc = auc(
            false_positive_rate,
            true_positive_rate,
        )

        roc_auc_values[
            class_name
        ] = float(class_auc)

        roc_axis.plot(
            false_positive_rate,
            true_positive_rate,
            label=(
                f"{class_name} "
                f"(AUC = {class_auc:.4f})"
            ),
        )

    (
        micro_false_positive_rate,
        micro_true_positive_rate,
        _,
    ) = roc_curve(
        binarized_true_labels.ravel(),
        predicted_probabilities.ravel(),
    )

    micro_auc = auc(
        micro_false_positive_rate,
        micro_true_positive_rate,
    )

    roc_auc_values[
        "micro_average"
    ] = float(micro_auc)

    roc_axis.plot(
        micro_false_positive_rate,
        micro_true_positive_rate,
        linestyle="--",
        label=(
            "Micro-average "
            f"(AUC = {micro_auc:.4f})"
        ),
    )

    roc_axis.plot(
        [0, 1],
        [0, 1],
        linestyle=":",
    )

    roc_axis.set_title(
        "StellarX Multi-Class ROC Curves"
    )

    roc_axis.set_xlabel(
        "False Positive Rate"
    )

    roc_axis.set_ylabel(
        "True Positive Rate"
    )

    roc_axis.legend(
        loc="lower right"
    )

    roc_axis.grid(
        alpha=0.25
    )

    roc_figure.tight_layout()

    roc_figure.savefig(
        EVALUATION_OUTPUT_DIR
        / "roc_curves.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(roc_figure)

    save_json(
        EVALUATION_OUTPUT_DIR
        / "roc_auc_values.json",
        roc_auc_values,
    )

    # -----------------------------------------------------
    # Precision–recall curves
    # -----------------------------------------------------

    pr_figure, pr_axis = plt.subplots(
        figsize=(9, 7)
    )

    average_precision_values = {}

    for class_index, class_name in enumerate(
        CLASS_NAMES
    ):
        (
            precision_values,
            recall_values,
            _,
        ) = precision_recall_curve(
            binarized_true_labels[
                :,
                class_index,
            ],
            predicted_probabilities[
                :,
                class_index,
            ],
        )

        class_average_precision = auc(
            recall_values,
            precision_values,
        )

        average_precision_values[
            class_name
        ] = float(
            class_average_precision
        )

        pr_axis.plot(
            recall_values,
            precision_values,
            label=(
                f"{class_name} "
                f"(AP = "
                f"{class_average_precision:.4f})"
            ),
        )

    (
        micro_precision,
        micro_recall,
        _,
    ) = precision_recall_curve(
        binarized_true_labels.ravel(),
        predicted_probabilities.ravel(),
    )

    micro_average_precision = auc(
        micro_recall,
        micro_precision,
    )

    average_precision_values[
        "micro_average"
    ] = float(
        micro_average_precision
    )

    pr_axis.plot(
        micro_recall,
        micro_precision,
        linestyle="--",
        label=(
            "Micro-average "
            f"(AP = "
            f"{micro_average_precision:.4f})"
        ),
    )

    pr_axis.set_title(
        "StellarX Precision–Recall Curves"
    )

    pr_axis.set_xlabel(
        "Recall"
    )

    pr_axis.set_ylabel(
        "Precision"
    )

    pr_axis.legend(
        loc="lower left"
    )

    pr_axis.grid(
        alpha=0.25
    )

    pr_figure.tight_layout()

    pr_figure.savefig(
        EVALUATION_OUTPUT_DIR
        / "precision_recall_curves.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(pr_figure)

    save_json(
        EVALUATION_OUTPUT_DIR
        / "average_precision_values.json",
        average_precision_values,
    )

    # -----------------------------------------------------
    # Training-history diagrams
    # -----------------------------------------------------

    frozen_history_path = (
        TRAINING_OUTPUT_DIR
        / "frozen_history.json"
    )

    fine_tune_history_path = (
        TRAINING_OUTPUT_DIR
        / "fine_tune_history.json"
    )

    if (
        frozen_history_path.exists()
        and fine_tune_history_path.exists()
    ):
        with frozen_history_path.open(
            "r",
            encoding="utf-8",
        ) as history_file:
            frozen_history = json.load(
                history_file
            )

        with fine_tune_history_path.open(
            "r",
            encoding="utf-8",
        ) as history_file:
            fine_tune_history = json.load(
                history_file
            )

        combined_history = {}

        history_keys = (
            set(frozen_history.keys())
            | set(fine_tune_history.keys())
        )

        for key in history_keys:
            combined_history[key] = (
                frozen_history.get(
                    key,
                    [],
                )
                + fine_tune_history.get(
                    key,
                    [],
                )
            )

        fine_tune_start_epoch = len(
            frozen_history.get(
                "accuracy",
                [],
            )
        )

        history_pairs = [
            (
                "accuracy",
                "val_accuracy",
                (
                    "Training and Validation "
                    "Accuracy"
                ),
                "Accuracy",
                (
                    "training_validation_"
                    "accuracy.png"
                ),
            ),
            (
                "loss",
                "val_loss",
                (
                    "Training and Validation "
                    "Loss"
                ),
                "Loss",
                (
                    "training_validation_"
                    "loss.png"
                ),
            ),
            (
                "precision",
                "val_precision",
                (
                    "Training and Validation "
                    "Precision"
                ),
                "Precision",
                (
                    "training_validation_"
                    "precision.png"
                ),
            ),
            (
                "recall",
                "val_recall",
                (
                    "Training and Validation "
                    "Recall"
                ),
                "Recall",
                (
                    "training_validation_"
                    "recall.png"
                ),
            ),
        ]

        for (
            training_key,
            validation_key,
            title,
            y_axis_label,
            filename,
        ) in history_pairs:
            if (
                training_key not in combined_history
                or validation_key
                not in combined_history
            ):
                continue

            epochs = range(
                1,
                len(
                    combined_history[
                        training_key
                    ]
                )
                + 1,
            )

            figure, axis = plt.subplots(
                figsize=(9, 6)
            )

            axis.plot(
                epochs,
                combined_history[
                    training_key
                ],
                label="Training",
            )

            axis.plot(
                epochs,
                combined_history[
                    validation_key
                ],
                label="Validation",
            )

            if fine_tune_start_epoch > 0:
                axis.axvline(
                    x=(
                        fine_tune_start_epoch
                        + 0.5
                    ),
                    linestyle="--",
                    label="Fine-tuning begins",
                )

            axis.set_title(title)
            axis.set_xlabel("Epoch")
            axis.set_ylabel(y_axis_label)
            axis.legend()
            axis.grid(alpha=0.25)

            figure.tight_layout()

            figure.savefig(
                EVALUATION_OUTPUT_DIR
                / filename,
                dpi=300,
                bbox_inches="tight",
            )

            plt.close(figure)

    else:
        print(
            "\nTraining-history files were "
            "not found. History diagrams "
            "were skipped."
        )

    # -----------------------------------------------------
    # Save prediction arrays
    # -----------------------------------------------------

    np.save(
        EVALUATION_OUTPUT_DIR
        / "true_class_indices.npy",
        true_class_indices,
    )

    np.save(
        EVALUATION_OUTPUT_DIR
        / "predicted_class_indices.npy",
        predicted_class_indices,
    )

    np.save(
        EVALUATION_OUTPUT_DIR
        / "predicted_probabilities.npy",
        predicted_probabilities,
    )

    # -----------------------------------------------------
    # Final summary
    # -----------------------------------------------------

    print(
        "\nEvaluation completed successfully."
    )

    print(
        f"Results saved to: "
        f"{EVALUATION_OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()