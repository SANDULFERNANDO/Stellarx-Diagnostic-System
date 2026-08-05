from pathlib import Path

from PIL import Image, UnidentifiedImageError


DATASET_ROOT = Path.home() / "Desktop" / "dataset"

SPLITS = ["train", "validation", "test"]
CLASSES = ["Eczema", "Leishmaniasis", "Tinea"]

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


def main() -> None:
    total_files = 0
    valid_images = 0
    invalid_images = []
    unsupported_files = []

    print("New dataset audit")
    print("=" * 70)

    for split_name in SPLITS:
        for class_name in CLASSES:
            folder = DATASET_ROOT / split_name / class_name

            if not folder.exists():
                print(f"Missing folder: {folder}")
                continue

            folder_valid = 0
            folder_invalid = 0
            folder_unsupported = 0

            for file_path in folder.iterdir():
                if not file_path.is_file():
                    continue

                total_files += 1

                if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                    unsupported_files.append(str(file_path))
                    folder_unsupported += 1
                    continue

                try:
                    with Image.open(file_path) as image:
                        image.verify()

                    # Reopen after verify to confirm the pixels can be loaded.
                    with Image.open(file_path) as image:
                        image.convert("RGB").load()

                    valid_images += 1
                    folder_valid += 1

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
                    folder_invalid += 1

            print(
                f"{split_name} / {class_name}: "
                f"valid={folder_valid}, "
                f"invalid={folder_invalid}, "
                f"unsupported={folder_unsupported}"
            )

    print("\n" + "=" * 70)
    print(f"Total files: {total_files}")
    print(f"Valid images: {valid_images}")
    print(f"Invalid images: {len(invalid_images)}")
    print(f"Unsupported files: {len(unsupported_files)}")

    if invalid_images:
        print("\nInvalid images:")

        for item in invalid_images:
            print(f"- {item['path']}")
            print(f"  Error: {item['error']}")

    if unsupported_files:
        print("\nUnsupported files:")

        for file_path in unsupported_files:
            print(f"- {file_path}")


if __name__ == "__main__":
    main()