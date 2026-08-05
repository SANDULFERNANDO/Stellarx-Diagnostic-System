from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SPLITS = {
    "Train": PROJECT_ROOT / "processed_dataset" / "train",
    "Validation": PROJECT_ROOT / "processed_dataset" / "validation",
    "Test": PROJECT_ROOT / "processed_dataset" / "test",
}

VALID_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}

OUTPUT_DIR = PROJECT_ROOT / "ml_outputs" / "dataset_analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def count_images(folder: Path) -> dict:
    counts = {}

    for class_folder in sorted(folder.iterdir()):
        if not class_folder.is_dir():
            continue

        counts[class_folder.name] = sum(
            1
            for file_path in class_folder.iterdir()
            if (
                file_path.is_file()
                and file_path.suffix.lower() in VALID_EXTENSIONS
            )
        )

    return counts


split_counts = {
    split_name: count_images(split_folder)
    for split_name, split_folder in SPLITS.items()
}

class_names = ["Eczema", "Leishmaniasis", "Tinea"]

x_positions = range(len(class_names))
bar_width = 0.24

figure, axis = plt.subplots(figsize=(10, 6))

for index, split_name in enumerate(SPLITS):
    values = [
        split_counts[split_name].get(class_name, 0)
        for class_name in class_names
    ]

    positions = [
        position + index * bar_width
        for position in x_positions
    ]

    bars = axis.bar(
        positions,
        values,
        width=bar_width,
        label=split_name,
    )

    axis.bar_label(
        bars,
        padding=3,
        fontsize=9,
    )

axis.set_title("StellarX Dataset Class Distribution")
axis.set_xlabel("Skin lesion class")
axis.set_ylabel("Number of images")

axis.set_xticks(
    [
        position + bar_width
        for position in x_positions
    ]
)

axis.set_xticklabels(class_names)
axis.legend()

figure.tight_layout()

output_file = (
    OUTPUT_DIR
    / "class_distribution.png"
)

figure.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight",
)

plt.show()

print("\nDataset counts")

for split_name, counts in split_counts.items():
    print(f"\n{split_name}")

    for class_name in class_names:
        print(
            f"{class_name}: "
            f"{counts.get(class_name, 0)}"
        )

print(f"\nDiagram saved to: {output_file}")