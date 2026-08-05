from collections import defaultdict
from hashlib import sha256
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SPLITS = {
    "train": PROJECT_ROOT / "train",
    "validation": PROJECT_ROOT / "validation",
    "test": PROJECT_ROOT / "test",
}

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


split_hashes = {}

for split_name, split_directory in SPLITS.items():
    print(f"Scanning {split_name}...")
    split_hashes[split_name] = collect_hashes(split_directory)


comparisons = [
    ("train", "validation"),
    ("train", "test"),
    ("validation", "test"),
]

print("\nCross-split leakage results")
print("=" * 60)

total_shared_groups = 0

for first_split, second_split in comparisons:
    shared_hashes = (
        set(split_hashes[first_split])
        & set(split_hashes[second_split])
    )

    total_shared_groups += len(shared_hashes)

    first_files = sum(
        len(split_hashes[first_split][image_hash])
        for image_hash in shared_hashes
    )

    second_files = sum(
        len(split_hashes[second_split][image_hash])
        for image_hash in shared_hashes
    )

    print(
        f"\n{first_split.upper()} vs "
        f"{second_split.upper()}"
    )
    print(f"Shared groups: {len(shared_hashes)}")
    print(f"{first_split} matching files: {first_files}")
    print(f"{second_split} matching files: {second_files}")


print("\n" + "=" * 60)
print(f"Total shared groups: {total_shared_groups}")

if total_shared_groups == 0:
    print("No exact leakage found across any split.")
else:
    print("Leakage was detected.")