from pathlib import Path
import random
import shutil


PROJECT_ROOT = Path(__file__).resolve().parent.parent

TRAIN_DIR = PROJECT_ROOT / "train"
VALIDATION_DIR = PROJECT_ROOT / "validation"

VALID_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}

VALIDATION_RATIO = 0.20
RANDOM_SEED = 42


random.seed(RANDOM_SEED)

print("Creating validation split")
print("=" * 60)

for class_folder in sorted(TRAIN_DIR.iterdir()):
    if not class_folder.is_dir():
        continue

    image_files = [
        file_path
        for file_path in sorted(class_folder.iterdir())
        if (
            file_path.is_file()
            and file_path.suffix.lower() in VALID_EXTENSIONS
        )
    ]

    random.shuffle(image_files)

    validation_count = round(
        len(image_files) * VALIDATION_RATIO
    )

    selected_files = image_files[:validation_count]

    destination_class = VALIDATION_DIR / class_folder.name
    destination_class.mkdir(
        parents=True,
        exist_ok=True,
    )

    for source_file in selected_files:
        destination_file = destination_class / source_file.name

        shutil.move(
            str(source_file),
            str(destination_file),
        )

    print(
        f"{class_folder.name}: "
        f"moved {len(selected_files)} images"
    )

print("\nValidation split completed.")
print(f"Random seed: {RANDOM_SEED}")
print(f"Validation ratio: {VALIDATION_RATIO}")