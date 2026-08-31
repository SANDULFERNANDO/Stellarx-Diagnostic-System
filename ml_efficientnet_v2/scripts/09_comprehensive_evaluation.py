import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import tensorflow as tf
from sklearn.metrics import (
    confusion_matrix, classification_report, roc_curve, auc, 
    precision_recall_curve, average_precision_score, accuracy_score,
    precision_score, recall_score, f1_score
)
from sklearn.preprocessing import label_binarize

def main():
    workspace_dir = Path(__file__).resolve().parent.parent
    sys.path.append(str(workspace_dir))
    from src.data_utils import load_config
    
    config_path = workspace_dir / "config" / "training_config.json"
    model_path = workspace_dir / "artifacts" / "models" / "efficientnet_final.keras"
    test_dir = workspace_dir / "processed_data" / "test"
    
    # Create Output Directories
    eval_dir = workspace_dir / "artifacts" / "plots" / "evaluation"
    others_dir = workspace_dir / "artifacts" / "plots" / "others"
    eval_dir.mkdir(parents=True, exist_ok=True)
    others_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading config and model...")
    config = load_config(config_path)
    classes = config["classes"]
    img_size = tuple(config["image_size"])
    batch_size = config["batch_size"]
    
    model = tf.keras.models.load_model(str(model_path))
    
    print("Loading untouched test dataset...")
    test_ds = tf.keras.preprocessing.image_dataset_from_directory(
        test_dir,
        seed=42,
        image_size=img_size,
        batch_size=batch_size,
        shuffle=False # CRITICAL: MUST NOT SHUFFLE FOR EVALUATION
    )
    
    print("Generating predictions...")
    y_true = []
    y_pred_probs = []
    
    for images, labels in test_ds:
        y_true.extend(labels.numpy())
        preds = model.predict(images, verbose=0)
        y_pred_probs.extend(preds)
        
    y_true = np.array(y_true)
    y_pred_probs = np.array(y_pred_probs)
    y_pred_classes = np.argmax(y_pred_probs, axis=1)
    
    # --- 5 & 6. Confusion Matrices ---
    print("Generating Confusion Matrices...")
    cm = confusion_matrix(y_true, y_pred_classes)
    
    # Raw Counts
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
    plt.title('EfficientNetB3 - Confusion Matrix (Counts)', fontsize=16, pad=15)
    plt.ylabel('Actual Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    plt.savefig(eval_dir / "EfficientNetB3_CM_Counts.png", dpi=300)
    plt.close()
    
    # Normalized
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm_norm, annot=True, fmt='.2%', cmap='Blues', xticklabels=classes, yticklabels=classes)
    plt.title('EfficientNetB3 - Normalized Confusion Matrix', fontsize=16, pad=15)
    plt.ylabel('Actual Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    plt.savefig(eval_dir / "EfficientNetB3_CM_Normalized.png", dpi=300)
    plt.close()
    
    # --- 7. Multi-Class ROC Curves ---
    print("Generating ROC Curves...")
    y_true_bin = label_binarize(y_true, classes=[0, 1, 2, 3])
    n_classes = len(classes)
    
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    
    plt.figure(figsize=(10, 8))
    colors = ['blue', 'red', 'green', 'orange']
    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_true_bin[:, i], y_pred_probs[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])
        plt.plot(fpr[i], tpr[i], color=colors[i], lw=2,
                 label=f'{classes[i]} (AUC = {roc_auc[i]:.3f})')
                 
    plt.plot([0, 1], [0, 1], 'k--', lw=2)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('EfficientNetB3 - Multi-Class ROC Curves', fontsize=16, pad=15)
    plt.legend(loc="lower right", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(eval_dir / "EfficientNetB3_ROC_Curves.png", dpi=300)
    plt.close()
    
    # --- 8. Precision-Recall Curves ---
    print("Generating Precision-Recall Curves...")
    precision_dict = dict()
    recall_dict = dict()
    average_precision = dict()
    
    plt.figure(figsize=(10, 8))
    for i in range(n_classes):
        precision_dict[i], recall_dict[i], _ = precision_recall_curve(y_true_bin[:, i], y_pred_probs[:, i])
        average_precision[i] = average_precision_score(y_true_bin[:, i], y_pred_probs[:, i])
        plt.plot(recall_dict[i], precision_dict[i], color=colors[i], lw=2,
                 label=f'{classes[i]} (AP = {average_precision[i]:.3f})')
                 
    plt.xlabel('Recall', fontsize=12)
    plt.ylabel('Precision', fontsize=12)
    plt.title('EfficientNetB3 - Precision-Recall Curves', fontsize=16, pad=15)
    plt.legend(loc="lower left", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(eval_dir / "EfficientNetB3_PR_Curves.png", dpi=300)
    plt.close()
    
    # --- 9. Per-Class Performance Graph ---
    print("Generating Per-Class Performance Bar Chart...")
    report = classification_report(y_true, y_pred_classes, target_names=classes, output_dict=True)
    
    metrics_data = {
        'Precision': [report[c]['precision'] for c in classes],
        'Recall': [report[c]['recall'] for c in classes],
        'F1-Score': [report[c]['f1-score'] for c in classes]
    }
    
    x = np.arange(len(classes))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 7))
    rects1 = ax.bar(x - width, metrics_data['Precision'], width, label='Precision', color='#1f77b4')
    rects2 = ax.bar(x, metrics_data['Recall'], width, label='Recall', color='#ff7f0e')
    rects3 = ax.bar(x + width, metrics_data['F1-Score'], width, label='F1-Score', color='#2ca02c')
    
    ax.set_ylabel('Scores', fontsize=12)
    ax.set_title('EfficientNetB3 - Per-Class Classification Performance', fontsize=16, pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(classes, fontsize=12)
    ax.legend(fontsize=12, loc='lower right')
    ax.set_ylim(0, 1.1)
    
    # Add values on top of bars
    for rects in [rects1, rects2, rects3]:
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)
                        
    plt.tight_layout()
    plt.savefig(eval_dir / "EfficientNetB3_PerClass_Metrics.png", dpi=300)
    plt.close()
    
    # --- 11. Others / Invalid-Image Performance ---
    print("Generating Others Rejection Performance...")
    others_idx = classes.index("others")
    others_true = (y_true == others_idx)
    others_pred = (y_pred_classes == others_idx)
    
    total_others = np.sum(others_true)
    correct_others = cm[others_idx, others_idx]
    
    valid_diseases_idx = [i for i in range(len(classes)) if i != others_idx]
    valid_predicted_as_others = sum(cm[i, others_idx] for i in valid_diseases_idx)
    
    others_summary = {
        "Total Others Images": int(total_others),
        "Correctly Rejected (Predicted as Others)": int(correct_others),
        "Others Recall (True Negative Rate for diseases)": float(report["others"]["recall"]),
        "Others Precision": float(report["others"]["precision"]),
        "Others F1-Score": float(report["others"]["f1-score"]),
        "Valid Disease Images Incorrectly Rejected": int(valid_predicted_as_others),
        "Others Images Incorrectly Predicted as Eczema": int(cm[others_idx, classes.index("Eczema")]),
        "Others Images Incorrectly Predicted as Leishmaniasis": int(cm[others_idx, classes.index("Leishmaniasis")]),
        "Others Images Incorrectly Predicted as Tinea": int(cm[others_idx, classes.index("Tinea")]),
    }
    
    # Save others summary as a nice table figure
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis('tight')
    ax.axis('off')
    table_data = [[k, v] for k, v in others_summary.items()]
    table = ax.table(cellText=table_data, colLabels=["Metric", "Value"], loc='center', cellLoc='left')
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.8)
    plt.title('EfficientNetB3 - Others Class Rejection Performance', fontsize=14, pad=20)
    plt.tight_layout()
    plt.savefig(others_dir / "EfficientNetB3_Others_Summary.png", dpi=300)
    plt.close()
    
    # --- 13. Final Metrics Summary ---
    print("Generating Final JSON Summary...")
    
    # Calculate some extra metrics
    total_correct = np.sum(np.diag(cm))
    total_incorrect = len(y_true) - total_correct
    
    # Find most common misclassification
    np.fill_diagonal(cm, 0)
    max_err_idx = np.unravel_index(np.argmax(cm, axis=None), cm.shape)
    most_common_err = f"Actual {classes[max_err_idx[0]]} predicted as {classes[max_err_idx[1]]} ({cm[max_err_idx]} times)"
    
    final_summary = {
        "model_name": "EfficientNetB3",
        "number_of_classes": n_classes,
        "class_names": classes,
        "test_dataset_size": len(y_true),
        "test_accuracy": float(accuracy_score(y_true, y_pred_classes)),
        "macro_precision": float(report["macro avg"]["precision"]),
        "macro_recall": float(report["macro avg"]["recall"]),
        "macro_f1": float(report["macro avg"]["f1-score"]),
        "weighted_precision": float(report["weighted avg"]["precision"]),
        "weighted_recall": float(report["weighted avg"]["recall"]),
        "weighted_f1": float(report["weighted avg"]["f1-score"]),
        "per_class_metrics": report,
        "roc_auc_values": {classes[i]: float(roc_auc[i]) for i in range(n_classes)},
        "average_precision_values": {classes[i]: float(average_precision[i]) for i in range(n_classes)},
        "total_correct": int(total_correct),
        "total_incorrect": int(total_incorrect),
        "most_common_error": most_common_err,
        "others_rejection_metrics": others_summary
    }
    
    # Write JSON
    with open(eval_dir / "EfficientNetB3_Final_Metrics.json", "w") as f:
        json.dump(final_summary, f, indent=4)
        
    print("All evaluation plots and metrics successfully generated!")

if __name__ == "__main__":
    main()
