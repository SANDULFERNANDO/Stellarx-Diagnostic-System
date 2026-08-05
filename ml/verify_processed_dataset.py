from pathlib import Path

from PIL import Image, UnidentifiedImageError


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_ROOT = (
    PROJECT_ROOT
    / "processed_dataset_new_run"
)


# ---------------------------------------------------------
# Dataset configuration
# ---------------------------------------------------------

SPLITS = [
    "train",
    "validation",
    "test",
]

CLASSES = [
    "Eczema",
    "Leishmaniasis",
    "Tinea",
]

EXPECTED_SIZE = (224, 224)
EXPECTED_MODE = "RGB"

VALID_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


# ---------------------------------------------------------
# Main verification
# ---------------------------------------------------------

def main() -> None:
    print("StellarX processed dataset verification")
    print("=" * 70)

    if not PROCESSED_ROOT.exists():
        raise FileNotFoundError(
            f"Processed dataset was not found: "
            f"{PROCESSED_ROOT}"
        )

    total_images = 0
    valid_images = 0

    invalid_images = []
    wrong_dimensions = []
    wrong_color_modes = []
    unsupported_files = []

    for split_name in SPLITS:
        print(f"\nChecking {split_name.upper()}")
        print("-" * 70)

        split_total = 0

        for class_name in CLASSES:
            class_folder = (
                PROCESSED_ROOT
                / split_name
                / class_name
            )

            if not class_folder.exists():
                raise FileNotFoundError(
                    f"Class folder was not found: "
                    f"{class_folder}"
                )

            class_total = 0
            class_valid = 0

            for file_path in sorted(
                class_folder.iterdir(),
                key=lambda path: path.name.lower(),
            ):
                if not file_path.is_file():
                    continue

                total_images += 1
                split_total += 1
                class_total += 1

                if (
                    file_path.suffix.lower()
                    not in VALID_EXTENSIONS
                ):
                    unsupported_files.append(
                        str(file_path)
                    )
                    continue

                try:
                    with Image.open(file_path) as image:
                        image.load()

                        image_size = image.size
                        image_mode = image.mode

                    has_problem = False

                    if image_size != EXPECTED_SIZE:
                        wrong_dimensions.append(
                            {
                                "path": str(file_path),
                                "actual_size": image_size,
                            }
                        )
                        has_problem = True

                    if image_mode != EXPECTED_MODE:
                        wrong_color_modes.append(
                            {
                                "path": str(file_path),
                                "actual_mode": image_mode,
                            }
                        )
                        has_problem = True

                    if not has_problem:
                        valid_images += 1
                        class_valid += 1

                except (
                    UnidentifiedImageError,
                    OSError,
                    ValueError,
                ) as error:
                    invalid_images.append(
                        {
                            "path": str(file_path),
                            "error": str(error),
                        }
                    )

            print(
                f"{class_name}: "
                f"total={class_total}, "
                f"valid={class_valid}"
            )

        print(
            f"{split_name.upper()} total: "
            f"{split_total}"
        )

    print("\n" + "=" * 70)
    print("Verification summary")
    print("=" * 70)

    print(
        f"Total images: "
        f"{total_images}"
    )

    print(
        f"Valid images: "
        f"{valid_images}"
    )

    print(
        f"Invalid images: "
        f"{len(invalid_images)}"
    )

    print(
        f"Wrong dimensions: "
        f"{len(wrong_dimensions)}"
    )

    print(
        f"Wrong color mode: "
        f"{len(wrong_color_modes)}"
    )

    print(
        f"Unsupported files: "
        f"{len(unsupported_files)}"
    )

    print(
        f"Expected image size: "
        f"{EXPECTED_SIZE}"
    )

    print(
        f"Expected color mode: "
        f"{EXPECTED_MODE}"
    )

    print(
        f"Dataset location: "
        f"{PROCESSED_ROOT}"
    )

    if invalid_images:
        print("\nInvalid images:")

        for item in invalid_images:
            print(
                f"- {item['path']}"
            )
            print(
                f"  Error: {item['error']}"
            )

    if wrong_dimensions:
        print("\nImages with wrong dimensions:")

        for item in wrong_dimensions:
            print(
                f"- {item['path']} "
                f"| size={item['actual_size']}"
            )

    if wrong_color_modes:
        print("\nImages with wrong color mode:")

        for item in wrong_color_modes:
            print(
                f"- {item['path']} "
                f"| mode={item['actual_mode']}"
            )

    if unsupported_files:
        print("\nUnsupported files:")

        for file_path in unsupported_files:
            print(f"- {file_path}")

    if (
        total_images == 3827
        and valid_images == 3827
        and not invalid_images
        and not wrong_dimensions
        and not wrong_color_modes
        and not unsupported_files
    ):
        print(
            "\nProcessed dataset verification passed."
        )
    else:
        print(
            "\nWarning: processed dataset verification "
            "did not fully pass."
        )


if __name__ == "__main__":
    main()