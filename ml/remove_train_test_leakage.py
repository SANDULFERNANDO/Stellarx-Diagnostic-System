from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import shutil


PROJECT_ROOT = Path(__file__).resolve().parent.parent

TRAIN_DIR = PROJECT_ROOT / "train"
TEST_DIR = PROJECT_ROOT / "test"

BACKUP_DIR = (
    PROJECT_ROOT
    / "dataset_backups"
    / "train_test_leakage"
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

    for file_path in split_directory.rglob("*"):
        if (
            file_path.is_file()
            and file_path.suffix.lower() in VALID_EXTENSIONS
        ):
            image_hash = calculate_hash(file_path)
            hash_groups[image_hash].append(file_path)

    return hash_groups


train_hashes = collect_hashes(TRAIN_DIR)
test_hashes = collect_hashes(TEST_DIR)

shared_hashes = set(train_hashes) & set(test_hashes)

moved_files = 0

for image_hash in shared_hashes:
    for train_file in train_hashes[image_hash]:
        relative_path = train_file.relative_to(TRAIN_DIR)
        destination = BACKUP_DIR / relative_path

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
            str(train_file),
            str(destination),
        )

        print(
            f"Moved: {relative_path}"
        )

        moved_files += 1


print("\n" + "=" * 60)
print(f"Shared hash groups: {len(shared_hashes)}")
print(f"Training files moved: {moved_files}")
print(f"Backup folder: {BACKUP_DIR}")