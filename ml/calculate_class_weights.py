from pathlib import Path

import numpy as np
from sklearn.utils.class_weight import compute_class_weight


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRAIN_DIR = PROJECT_ROOT / "processed_dataset" / "train"

VALID_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


class_names = sorted(
    folder.name
    for folder in TRAIN_DIR.iterdir()
    if folder.is_dir()
)

labels = []

for class_index, class_name in enumerate(class_names):
    class_folder = TRAIN_DIR / class_name

    image_count = sum(
        1
        for file_path in class_folder.iterdir()
        if (
            file_path.is_file()
            and file_path.suffix.lower() in VALID_EXTENSIONS
        )
    )

    labels.extend([class_index] * image_count)


labels = np.array(labels)

weights = compute_class_weight(
    class_weight="balanced",
    classes=np.arange(len(class_names)),
    y=labels,
)

class_weights = {
    index: float(weight)
    for index, weight in enumerate(weights)
}


print("Class names:")
print(class_names)

print("\nClass weights:")

for index, class_name in enumerate(class_names):
    print(
        f"{index} - {class_name}: "
        f"{class_weights[index]:.4f}"
    )

print("\nDictionary for model.fit()")
print(class_weights)