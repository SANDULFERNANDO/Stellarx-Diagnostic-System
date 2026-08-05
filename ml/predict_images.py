from pathlib import Path
import argparse
import json

import numpy as np
import tensorflow as tf
from PIL import Image, ImageFilter, UnidentifiedImageError


# ---------------------------------------------------------
# Paths and configuration
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "models_new_run"
    / "stellarx_efficientnetb0_new_final.keras"
)

IMAGE_SIZE = (224, 224)

MIN_IMAGES = 1
MAX_IMAGES = 5

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


# ---------------------------------------------------------
# Validate uploaded image paths
# ---------------------------------------------------------

def validate_image(image_path: Path) -> None:
    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    if not image_path.is_file():
        raise ValueError(
            f"Path is not a file: {image_path}"
        )

    if image_path.suffix.lower() not in VALID_EXTENSIONS:
        raise ValueError(
            f"Unsupported image format: {image_path.name}. "
            f"Supported formats: {sorted(VALID_EXTENSIONS)}"
        )

    try:
        with Image.open(image_path) as image:
            image.verify()

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
    ) as error:
        raise ValueError(
            f"Invalid or corrupted image "
            f"'{image_path.name}': {error}"
        ) from error


def validate_image_count(image_paths: list[Path]) -> None:
    image_count = len(image_paths)

    if image_count < MIN_IMAGES:
        raise ValueError(
            "At least one image is required."
        )

    if image_count > MAX_IMAGES:
        raise ValueError(
            f"A maximum of {MAX_IMAGES} images is allowed. "
            f"Received: {image_count}"
        )


# ---------------------------------------------------------
# Apply the same preprocessing used during training
# ---------------------------------------------------------

def preprocess_image(image_path: Path) -> np.ndarray:
    with Image.open(image_path) as image:
        image = image.convert("RGB")

        image = image.resize(
            IMAGE_SIZE,
            Image.Resampling.LANCZOS,
        )

        image = image.filter(
            ImageFilter.MedianFilter(size=3)
        )

        image_array = np.asarray(
            image,
            dtype=np.float32,
        )

    return image_array


def create_image_batch(
    image_paths: list[Path],
) -> np.ndarray:
    processed_images = [
        preprocess_image(image_path)
        for image_path in image_paths
    ]

    return np.stack(
        processed_images,
        axis=0,
    )


# ---------------------------------------------------------
# Predict all images in one batch
# ---------------------------------------------------------

def predict_images(
    model: tf.keras.Model,
    image_paths: list[Path],
) -> list[dict]:
    image_batch = create_image_batch(
        image_paths
    )

    batch_probabilities = model.predict(
        image_batch,
        verbose=0,
    )

    results = []

    for image_path, probabilities in zip(
        image_paths,
        batch_probabilities,
    ):
        predicted_index = int(
            np.argmax(probabilities)
        )

        predicted_class = CLASS_NAMES[
            predicted_index
        ]

        confidence = float(
            probabilities[predicted_index]
        )

        results.append(
            {
                "file_name": image_path.name,
                "file_path": str(image_path),
                "predicted_class": predicted_class,
                "confidence": confidence,
                "probabilities": {
                    class_name: float(
                        probabilities[class_index]
                    )
                    for class_index, class_name
                    in enumerate(CLASS_NAMES)
                },
            }
        )

    return results


# ---------------------------------------------------------
# Aggregate image predictions for a case-level summary
# ---------------------------------------------------------

def create_case_summary(
    image_results: list[dict],
) -> dict:
    probability_matrix = np.array(
        [
            [
                result["probabilities"][class_name]
                for class_name in CLASS_NAMES
            ]
            for result in image_results
        ],
        dtype=np.float32,
    )

    mean_probabilities = np.mean(
        probability_matrix,
        axis=0,
    )

    case_predicted_index = int(
        np.argmax(mean_probabilities)
    )

    case_predicted_class = CLASS_NAMES[
        case_predicted_index
    ]

    case_confidence = float(
        mean_probabilities[case_predicted_index]
    )

    predicted_classes = [
        result["predicted_class"]
        for result in image_results
    ]

    agreement_count = predicted_classes.count(
        case_predicted_class
    )

    agreement_ratio = (
        agreement_count / len(image_results)
    )

    return {
        "aggregation_method": (
            "Mean probability across uploaded images"
        ),
        "predicted_class": case_predicted_class,
        "confidence": case_confidence,
        "agreement_count": agreement_count,
        "total_images": len(image_results),
        "agreement_ratio": agreement_ratio,
        "mean_probabilities": {
            class_name: float(
                mean_probabilities[class_index]
            )
            for class_index, class_name
            in enumerate(CLASS_NAMES)
        },
    }


# ---------------------------------------------------------
# Print results
# ---------------------------------------------------------

def print_results(
    image_results: list[dict],
    case_summary: dict,
) -> None:
    print("\nStellarX multi-image prediction")
    print("=" * 70)

    for image_number, result in enumerate(
        image_results,
        start=1,
    ):
        print(
            f"\nImage {image_number}: "
            f"{result['file_name']}"
        )

        print(
            f"Predicted class: "
            f"{result['predicted_class']}"
        )

        print(
            f"Confidence: "
            f"{result['confidence'] * 100:.2f}%"
        )

        print("Class probabilities:")

        for class_name in CLASS_NAMES:
            probability = (
                result["probabilities"][class_name]
                * 100
            )

            print(
                f"  {class_name}: "
                f"{probability:.2f}%"
            )

    print("\n" + "=" * 70)
    print("Case-level summary")
    print("=" * 70)

    print(
        f"Aggregation: "
        f"{case_summary['aggregation_method']}"
    )

    print(
        f"Final image-model prediction: "
        f"{case_summary['predicted_class']}"
    )

    print(
        f"Final image-model confidence: "
        f"{case_summary['confidence'] * 100:.2f}%"
    )

    print(
        f"Image agreement: "
        f"{case_summary['agreement_count']}/"
        f"{case_summary['total_images']} "
        f"({case_summary['agreement_ratio'] * 100:.2f}%)"
    )

    print("Mean class probabilities:")

    for class_name in CLASS_NAMES:
        probability = (
            case_summary[
                "mean_probabilities"
            ][class_name]
            * 100
        )

        print(
            f"  {class_name}: "
            f"{probability:.2f}%"
        )


# ---------------------------------------------------------
# Main program
# ---------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Predict 1 to 5 skin-lesion images using "
            "the StellarX EfficientNetB0 model."
        )
    )

    parser.add_argument(
        "images",
        nargs="+",
        help=(
            "Paths to between 1 and 5 "
            "skin-lesion images."
        ),
    )

    parser.add_argument(
        "--json-output",
        type=str,
        default=None,
        help=(
            "Optional path for saving the full "
            "prediction result as JSON."
        ),
    )

    arguments = parser.parse_args()

    image_paths = [
        Path(image_path).expanduser().resolve()
        for image_path in arguments.images
    ]

    validate_image_count(
        image_paths
    )

    for image_path in image_paths:
        validate_image(
            image_path
        )

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_PATH}"
        )

    print("Loading StellarX model...")

    model = tf.keras.models.load_model(
        MODEL_PATH
    )

    image_results = predict_images(
        model,
        image_paths,
    )

    case_summary = create_case_summary(
        image_results
    )

    complete_result = {
        "image_count": len(image_results),
        "image_predictions": image_results,
        "case_summary": case_summary,
    }

    print_results(
        image_results,
        case_summary,
    )

    if arguments.json_output:
        output_path = Path(
            arguments.json_output
        ).expanduser().resolve()

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with output_path.open(
            "w",
            encoding="utf-8",
        ) as output_file:
            json.dump(
                complete_result,
                output_file,
                indent=4,
            )

        print(
            f"\nJSON result saved to: "
            f"{output_path}"
        )


if __name__ == "__main__":
    main()