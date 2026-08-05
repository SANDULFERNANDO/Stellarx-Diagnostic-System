from pathlib import Path

import matplotlib.pyplot as plt
import tensorflow as tf
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRAIN_DIR = PROJECT_ROOT / "processed_dataset" / "train"

OUTPUT_DIR = PROJECT_ROOT / "ml_outputs" / "augmentation"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_SIZE = (224, 224)
RANDOM_SEED = 42


data_augmentation = tf.keras.Sequential(
    [
        tf.keras.layers.RandomFlip(
            "horizontal",
            seed=RANDOM_SEED,
        ),
        tf.keras.layers.RandomRotation(
            0.08,
            seed=RANDOM_SEED,
        ),
        tf.keras.layers.RandomZoom(
            0.10,
            seed=RANDOM_SEED,
        ),
        tf.keras.layers.RandomTranslation(
            height_factor=0.05,
            width_factor=0.05,
            seed=RANDOM_SEED,
        ),
        tf.keras.layers.RandomContrast(
            0.10,
            seed=RANDOM_SEED,
        ),
    ],
    name="data_augmentation",
)


sample_file = next(
    file_path
    for file_path in sorted((TRAIN_DIR / "Tinea").iterdir())
    if file_path.is_file()
)

with Image.open(sample_file) as image:
    image = image.convert("RGB")
    image = image.resize(IMAGE_SIZE)

image_tensor = tf.convert_to_tensor(image)
image_tensor = tf.cast(image_tensor, tf.float32)
image_tensor = tf.expand_dims(image_tensor, axis=0)


figure, axes = plt.subplots(
    nrows=2,
    ncols=4,
    figsize=(12, 7),
)

axes = axes.flatten()

axes[0].imshow(image)
axes[0].set_title("Original")
axes[0].axis("off")


for index in range(1, 8):
    augmented = data_augmentation(
        image_tensor,
        training=True,
    )[0]

    augmented = tf.clip_by_value(
        augmented,
        0,
        255,
    )

    axes[index].imshow(
        tf.cast(augmented, tf.uint8)
    )

    axes[index].set_title(
        f"Augmented {index}"
    )

    axes[index].axis("off")


figure.suptitle(
    "StellarX Training Data Augmentation",
    fontsize=16,
)

figure.tight_layout()

output_file = (
    OUTPUT_DIR
    / "augmentation_examples.png"
)

figure.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight",
)

plt.close(figure)

print(f"Sample image: {sample_file}")
print(f"Diagram saved to: {output_file}")