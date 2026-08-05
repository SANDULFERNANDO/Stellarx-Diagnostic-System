from pathlib import Path

from PIL import Image, ImageFilter, UnidentifiedImageError


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCE_ROOT = Path.home() / "Desktop" / "dataset"

OUTPUT_ROOT = (
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

IMAGE_SIZE = (224, 224)

MEDIAN_FILTER_SIZE = 3

JPEG_QUALITY = 90

VALID_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


# ---------------------------------------------------------
# Preprocess one image
# ---------------------------------------------------------

def preprocess_image(
    source_file: Path,
    output_file: Path,
) -> None:
    with Image.open(source_file) as image:
        image = image.convert("RGB")

        image = image.resize(
            IMAGE_SIZE,
            Image.Resampling.LANCZOS,
        )

        image = image.filter(
            ImageFilter.MedianFilter(
                size=MEDIAN_FILTER_SIZE
            )
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        image.save(
            output_file,
            format="JPEG",
            quality=JPEG_QUALITY,
            optimize=True,
        )


# ---------------------------------------------------------
# Find valid source files
# ---------------------------------------------------------

def get_source_images(
    class_folder: Path,
) -> list[Path]:
    return sorted(
        [
            file_path
            for file_path in class_folder.iterdir()
            if file_path.is_file()
            and file_path.suffix.lower()
            in VALID_EXTENSIONS
        ],
        key=lambda path: path.name.lower(),
    )


# ---------------------------------------------------------
# Main preprocessing process
# ---------------------------------------------------------

def main() -> None:
    print("StellarX new dataset preprocessing")
    print("=" * 70)

    if not SOURCE_ROOT.exists():
        raise FileNotFoundError(
            f"Source dataset was not found: "
            f"{SOURCE_ROOT}"
        )

    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    grand_total = 0
    failed_files = []
    expected_files = 0

    for split_name in SPLITS:
        split_directory = (
            SOURCE_ROOT
            / split_name
        )

        if not split_directory.exists():
            raise FileNotFoundError(
                f"Split folder was not found: "
                f"{split_directory}"
            )

        print(
            f"\nProcessing {split_name.upper()}"
        )
        print("-" * 70)

        split_total = 0

        for class_name in CLASSES:
            class_folder = (
                split_directory
                / class_name
            )

            if not class_folder.exists():
                raise FileNotFoundError(
                    f"Class folder was not found: "
                    f"{class_folder}"
                )

            source_images = get_source_images(
                class_folder
            )

            expected_files += len(
                source_images
            )

            output_class_folder = (
                OUTPUT_ROOT
                / split_name
                / class_name
            )

            output_class_folder.mkdir(
                parents=True,
                exist_ok=True,
            )

            class_total = 0

            for image_number, source_file in enumerate(
                source_images,
                start=1,
            ):
                output_name = (
                    f"{class_name}_{split_name}_"
                    f"{image_number:04d}.jpg"
                )

                output_file = (
                    output_class_folder
                    / output_name
                )

                try:
                    preprocess_image(
                        source_file=source_file,
                        output_file=output_file,
                    )

                    class_total += 1
                    split_total += 1
                    grand_total += 1

                except (
                    UnidentifiedImageError,
                    OSError,
                    ValueError,
                ) as error:
                    failed_files.append(
                        {
                            "source": str(
                                source_file
                            ),
                            "error": str(error),
                        }
                    )

            print(
                f"{class_name}: "
                f"{class_total} processed"
            )

        print(
            f"{split_name.upper()} total: "
            f"{split_total}"
        )

    print("\n" + "=" * 70)
    print("Preprocessing summary")
    print("=" * 70)

    print(
        f"Source images found: "
        f"{expected_files}"
    )

    print(
        f"Successfully processed: "
        f"{grand_total}"
    )

    print(
        f"Failed images: "
        f"{len(failed_files)}"
    )

    print(
        f"Output folder: "
        f"{OUTPUT_ROOT}"
    )

    if failed_files:
        print("\nFailed files:")

        for failed_item in failed_files:
            print(
                f"- {failed_item['source']}"
            )

            print(
                f"  Error: "
                f"{failed_item['error']}"
            )

    if (
        grand_total == expected_files
        and not failed_files
    ):
        print(
            "\nAll source images were "
            "processed successfully."
        )
    else:
        print(
            "\nWarning: the number of processed "
            "images does not match the source total."
        )


if __name__ == "__main__":
    main()