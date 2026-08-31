import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
import json
from pathlib import Path

def plot_confusion_matrix(y_true, y_pred, classes, output_path):
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved confusion matrix plot to {output_path}")

def evaluate_others_class(y_true, y_pred, classes):
    """
    Specifically analyzes how the 'Others' class performs, as requested by the requirements.
    """
    others_idx = classes.index("others")
    
    # 1. How many Others images are correctly rejected
    true_others = (y_true == others_idx)
    correct_rejections = np.sum((y_true == others_idx) & (y_pred == others_idx))
    total_true_others = np.sum(true_others)
    
    # 2. How many valid disease images are incorrectly predicted as Others (False Rejections)
    true_disease = (y_true != others_idx)
    false_rejections = np.sum(true_disease & (y_pred == others_idx))
    
    # 3. Which Others images are incorrectly classified as diseases
    false_diseases = np.sum(true_others & (y_pred != others_idx))
    
    results = {
        "correct_rejections": int(correct_rejections),
        "total_true_others": int(total_true_others),
        "rejection_accuracy": float(correct_rejections / max(1, total_true_others)),
        "false_rejections_of_valid_diseases": int(false_rejections),
        "others_falsely_classified_as_disease": int(false_diseases)
    }
    
    return results

def generate_full_evaluation_report(y_true, y_pred, classes, output_dir):
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate sklearn classification report
    report_dict = classification_report(y_true, y_pred, target_names=classes, output_dict=True)
    report_str = classification_report(y_true, y_pred, target_names=classes)
    
    print("\n--- Classification Report ---")
    print(report_str)
    
    # Special "Others" evaluation
    if "others" in classes:
        others_eval = evaluate_others_class(y_true, y_pred, classes)
    else:
        others_eval = {}
        
    final_report = {
        "classification_metrics": report_dict,
        "others_evaluation": others_eval
    }
    
    report_path = out_dir / "final_evaluation_report.json"
    with open(report_path, "w") as f:
        json.dump(final_report, f, indent=4)
        
    print(f"\nSaved numerical report to {report_path}")
    
    # Plot confusion matrix
    cm_path = out_dir / "confusion_matrix.png"
    plot_confusion_matrix(y_true, y_pred, classes, cm_path)
