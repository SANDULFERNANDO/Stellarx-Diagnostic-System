from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = (
    PROJECT_ROOT
    / "ml_outputs_new_run"
    / "diagrams"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def add_box(
    axis,
    x,
    y,
    width,
    height,
    text,
    fontsize=10,
):
    box = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.02",
        linewidth=1.5,
        facecolor="white",
        edgecolor="black",
    )

    axis.add_patch(box)

    axis.text(
        x + width / 2,
        y + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        wrap=True,
    )


def add_down_arrow(
    axis,
    x,
    start_y,
    end_y,
):
    arrow = FancyArrowPatch(
        (x, start_y),
        (x, end_y),
        arrowstyle="-|>",
        mutation_scale=16,
        linewidth=1.5,
        color="black",
    )

    axis.add_patch(arrow)


# ---------------------------------------------------------
# Diagram 1: EfficientNetB0 architecture
# ---------------------------------------------------------

figure, axis = plt.subplots(
    figsize=(8, 12)
)

axis.set_xlim(0, 10)
axis.set_ylim(0, 16)
axis.axis("off")

architecture_steps = [
    (
        "Input Image\n224 × 224 × 3",
        14.2,
    ),
    (
        "Training Data Augmentation\n"
        "Horizontal Flip, Rotation, Zoom,\n"
        "Translation and Contrast",
        12.3,
    ),
    (
        "EfficientNetB0 Backbone\n"
        "ImageNet Pretrained Weights\n"
        "include_top = False",
        10.1,
    ),
    (
        "Convolutional Feature Maps\n"
        "Top Activation Layer",
        8.2,
    ),
    (
        "Global Average Pooling 2D",
        6.5,
    ),
    (
        "Dropout\nRate = 0.30",
        4.8,
    ),
    (
        "Dense Softmax Layer\n3 Output Neurons",
        3.1,
    ),
    (
        "Final Classes\n"
        "Eczema | Leishmaniasis | Tinea",
        1.1,
    ),
]

box_x = 2.0
box_width = 6.0
box_height = 1.15

for index, (text, y_position) in enumerate(
    architecture_steps
):
    add_box(
        axis,
        box_x,
        y_position,
        box_width,
        box_height,
        text,
        fontsize=10,
    )

    if index < len(architecture_steps) - 1:
        current_bottom = y_position
        next_top = (
            architecture_steps[index + 1][1]
            + box_height
        )

        add_down_arrow(
            axis,
            x=5.0,
            start_y=current_bottom,
            end_y=next_top,
        )


axis.set_title(
    "StellarX EfficientNetB0 Model Architecture",
    fontsize=16,
    pad=20,
)

architecture_output = (
    OUTPUT_DIR
    / "efficientnet_architecture.png"
)

figure.savefig(
    architecture_output,
    dpi=300,
    bbox_inches="tight",
)

plt.close(figure)


# ---------------------------------------------------------
# Diagram 2: Complete StellarX research pipeline
# ---------------------------------------------------------

figure, axis = plt.subplots(
    figsize=(10, 20)
)

axis.set_xlim(0, 12)
axis.set_ylim(0, 31)
axis.axis("off")

pipeline_steps = [
    "Dataset Collection\n"
    "3,827 Images: Eczema, Leishmaniasis and Tinea",

    "Dataset Audit\n"
    "Corrupted and Unsupported File Detection",

    "Exact Duplicate Detection and Removal",

    "Train–Test Leakage Detection and Removal",

    "Dataset Split\n"
    "Train: 2,679 | Validation: 573 | Test: 575",

    "Image Preprocessing\n"
    "RGB Conversion, Resize to 224 × 224,\n"
    "Median Filter 3 × 3, JPEG Standardization",

    "Processed Dataset Verification\n"
    "RGB, 224 × 224, Readable Images",

    "Class Distribution Analysis\n"
    "Train, Validation and Test Counts",

    "Class Weight Calculation\n"
    "Balanced Loss Contribution",

    "Training Data Augmentation\n"
    "Flip, Rotation, Zoom, Translation, Contrast",

    "EfficientNetB0 Transfer Learning\n"
    "ImageNet Weights and Frozen Backbone",

    "Fine-Tuning\n"
    "Upper Layers from Layer 200\n"
    "Batch Normalization Layers Frozen",

    "Independent Test Evaluation\n"
    "Accuracy, Precision, Recall and F1-Score",

    "Confusion Matrix Analysis\n"
    "Count-Based and Normalized",

    "ROC and Precision–Recall Analysis",

    "Prediction Analysis\n"
    "Correct, Incorrect and Tinea-Only Cases",

    "Grad-CAM Interpretation\n"
    "Correct and Incorrect Predictions",

    "Final Fine-Tuned Model Export\n"
    "stellarx_efficientnetb0_new_final.keras",

    "FastAPI Model Integration",

    "React Frontend Integration",

    "StellarX Diagnostic System",
]

box_x = 2.0
box_width = 8.0
box_height = 1.05

top_y = 29.2
vertical_gap = 1.35

for index, step_text in enumerate(
    pipeline_steps
):
    y_position = (
        top_y
        - index * vertical_gap
    )

    add_box(
        axis,
        box_x,
        y_position,
        box_width,
        box_height,
        step_text,
        fontsize=9.5,
    )

    if index < len(pipeline_steps) - 1:
        current_bottom = y_position
        next_top = (
            top_y
            - (index + 1) * vertical_gap
            + box_height
        )

        add_down_arrow(
            axis,
            x=6.0,
            start_y=current_bottom,
            end_y=next_top,
        )


axis.set_title(
    "StellarX Complete Research and Implementation Pipeline",
    fontsize=16,
    pad=20,
)

pipeline_output = (
    OUTPUT_DIR
    / "stellarx_research_pipeline.png"
)

figure.savefig(
    pipeline_output,
    dpi=300,
    bbox_inches="tight",
)

plt.close(figure)


# ---------------------------------------------------------
# Final output
# ---------------------------------------------------------

print(
    f"Architecture diagram saved to: "
    f"{architecture_output}"
)

print(
    f"Research pipeline diagram saved to: "
    f"{pipeline_output}"
)