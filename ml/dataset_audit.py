from pathlib import Path

from PIL import Image, UnidentifiedImageError


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_SPLITS = {
    "TRAIN": PROJECT_ROOT / "train",
    "TEST": PROJECT_ROOT / "test",
}

VALID_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


def inspect_split(split_name: str, split_directory: Path) -> int:
    print(f"\n{split_name}")
    print("=" * 55)

    if not split_directory.exists():
        print(f"Folder not found: {split_directory}")
        return 0

    split_total = 0
    corrupted_files = []
    unsupported_files = []

    for class_folder in sorted(split_directory.iterdir()):
        if not class_folder.is_dir():
            continue

        class_count = 0

        for file_path in class_folder.rglob("*"):
            if not file_path.is_file():
                continue

            if file_path.suffix.lower() not in VALID_EXTENSIONS:
                unsupported_files.append(file_path)
                continue

            try:
                with Image.open(file_path) as image:
                    image.verify()

                class_count += 1

            except (UnidentifiedImageError, OSError, ValueError) as error:
                corrupted_files.append(
                    (file_path, str(error))
                )

        split_total += class_count

        print(
            f"{class_folder.name}: "
            f"{class_count} valid images"
        )

    print("-" * 55)
    print(f"{split_name} total: {split_total}")
    print(f"Corrupted images: {len(corrupted_files)}")
    print(f"Unsupported files: {len(unsupported_files)}")

    if corrupted_files:
        print("\nCorrupted files:")

        for file_path, error in corrupted_files:
            print(f"{file_path} | {error}")

    if unsupported_files:
        print("\nUnsupported files:")

        for file_path in unsupported_files:
            print(file_path)

    return split_total


print("StellarX dataset audit")
print("=" * 55)

grand_total = 0

for split_name, split_directory in DATASET_SPLITS.items():
    grand_total += inspect_split(
        split_name,
        split_directory,
    )

print("\n" + "=" * 55)
print(f"Combined valid images: {grand_total}")
print(f"Project root: {PROJECT_ROOT}")