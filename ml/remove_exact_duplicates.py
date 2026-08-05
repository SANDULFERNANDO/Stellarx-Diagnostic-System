from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import shutil


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SPLITS = {
    "train": PROJECT_ROOT / "train",
    "test": PROJECT_ROOT / "test",
}

BACKUP_ROOT = (
    PROJECT_ROOT
    / "dataset_backups"
    / "exact_duplicates"
)

VALID_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


def calculate_hash(file_path: Path) -> str:
    with file_path.open("rb") as image_file:
        return sha256(image_file.read()).hexdigest()


def collect_hashes(split_directory: Path):
    hash_groups = defaultdict(list)

    for file_path in sorted(split_directory.rglob("*")):
        if (
            file_path.is_file()
            and file_path.suffix.lower() in VALID_EXTENSIONS
        ):
            image_hash = calculate_hash(file_path)
            hash_groups[image_hash].append(file_path)

    return hash_groups


def remove_duplicates(split_name: str, split_directory: Path):
    hash_groups = collect_hashes(split_directory)

    moved_files = 0
    duplicate_groups = 0

    for image_hash, file_paths in hash_groups.items():
        if len(file_paths) <= 1:
            continue

        duplicate_groups += 1

        original_file = file_paths[0]

        print(
            f"\nKeeping: "
            f"{original_file.relative_to(split_directory)}"
        )

        for duplicate_file in file_paths[1:]:
            relative_path = duplicate_file.relative_to(
                split_directory
            )

            destination = (
                BACKUP_ROOT
                / split_name
                / relative_path
            )

            destination.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            if destination.exists():
                destination = destination.with_name(
                    f"{destination.stem}_{image_hash[:8]}"
                    f"{destination.suffix}"
                )

            shutil.move(
                str(duplicate_file),
                str(destination),
            )

            print(f"Moved duplicate: {relative_path}")

            moved_files += 1

    print("\n" + "=" * 60)
    print(f"{split_name.upper()} duplicate groups: {duplicate_groups}")
    print(f"{split_name.upper()} files moved: {moved_files}")


for split_name, split_directory in SPLITS.items():
    remove_duplicates(
        split_name,
        split_directory,
    )

print("\nBackup folder:")
print(BACKUP_ROOT)