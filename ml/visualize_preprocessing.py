from pathlib import Path
import random

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageFilter


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRAIN_DIR = PROJECT_ROOT / "train"

OUTPUT_DIR = PROJECT_ROOT / "ml_outputs" / "preprocessing"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_SIZE = (224, 224)
RANDOM_SEED = 42

VALID_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


random.seed(RANDOM_SEED)

class_folders = sorted(
    folder
    for folder in TRAIN_DIR.iterdir()
    if folder.is_dir()
)

selected_images = []

for class_folder in class_folders:
    image_files = [
        file_path
        for file_path in class_folder.iterdir()
        if (
            file_path.is_file()
            and file_path.suffix.lower() in VALID_EXTENSIONS
        )
    ]

    if image_files:
        selected_images.append(
            random.choice(image_files)
        )


figure, axes = plt.subplots(
    nrows=len(selected_images),
    ncols=4,
    figsize=(14, 4 * len(selected_images)),
)

if len(selected_images) == 1:
    axes = np.expand_dims(axes, axis=0)


for row_index, source_file in enumerate(selected_images):
    with Image.open(source_file) as image:
        original = image.copy()

        rgb_image = image.convert("RGB")

        resized_image = rgb_image.resize(
            IMAGE_SIZE,
            Image.Resampling.LANCZOS,
        )

        filtered_image = resized_image.filter(
            ImageFilter.MedianFilter(size=3)
        )

    stages = [
        original,
        rgb_image,
        resized_image,
        filtered_image,
    ]

    stage_titles = [
        "Original",
        "RGB conversion",
        "Resize: 224 × 224",
        "Median filter: 3 × 3",
    ]

    class_name = source_file.parent.name

    for column_index, stage_image in enumerate(stages):
        axes[row_index, column_index].imshow(stage_image)
        axes[row_index, column_index].axis("off")

        axes[row_index, column_index].set_title(
            stage_titles[column_index]
        )

    axes[row_index, 0].set_ylabel(
        class_name,
        fontsize=12,
    )


figure.suptitle(
    "StellarX Image Preprocessing Stages",
    fontsize=16,
)

figure.tight_layout()

output_file = (
    OUTPUT_DIR
    / "preprocessing_stages.png"
)

figure.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight",
)

plt.show()

print(f"Diagram saved to: {output_file}")