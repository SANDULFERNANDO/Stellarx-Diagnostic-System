from collections import defaultdict
from hashlib import sha256
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

TRAIN_DIR = PROJECT_ROOT / "train"
TEST_DIR = PROJECT_ROOT / "test"

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


def print_duplicate_summary(
    split_name: str,
    split_directory: Path,
    hash_groups,
):
    duplicate_groups = [
        paths
        for paths in hash_groups.values()
        if len(paths) > 1
    ]

    extra_files = sum(
        len(paths) - 1
        for paths in duplicate_groups
    )

    cross_class_groups = 0

    for paths in duplicate_groups:
        class_names = {
            path.relative_to(split_directory).parts[0]
            for path in paths
        }

        if len(class_names) > 1:
            cross_class_groups += 1

    print(f"\n{split_name} duplicate check")
    print("=" * 60)
    print(f"Duplicate groups: {len(duplicate_groups)}")
    print(f"Extra duplicate files: {extra_files}")
    print(f"Cross-class duplicate groups: {cross_class_groups}")


print("Scanning training images...")
train_hashes = collect_hashes(TRAIN_DIR)

print("Scanning test images...")
test_hashes = collect_hashes(TEST_DIR)

print_duplicate_summary(
    "TRAIN",
    TRAIN_DIR,
    train_hashes,
)

print_duplicate_summary(
    "TEST",
    TEST_DIR,
    test_hashes,
)


shared_hashes = set(train_hashes) & set(test_hashes)

leaked_train_files = sum(
    len(train_hashes[image_hash])
    for image_hash in shared_hashes
)

leaked_test_files = sum(
    len(test_hashes[image_hash])
    for image_hash in shared_hashes
)

print("\nTrain–test leakage check")
print("=" * 60)
print(f"Shared image groups: {len(shared_hashes)}")
print(f"Matching training files: {leaked_train_files}")
print(f"Matching test files: {leaked_test_files}")