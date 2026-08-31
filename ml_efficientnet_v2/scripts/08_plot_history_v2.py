import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import os
import sys

def main():
    workspace_dir = Path(__file__).resolve().parent.parent
    csv_path = workspace_dir / "artifacts" / "metrics" / "training_history.csv"
    
    # Create new output directory
    output_dir = workspace_dir / "artifacts" / "plots" / "training"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_acc = output_dir / "EfficientNetB3_Training_Accuracy.png"
    output_loss = output_dir / "EfficientNetB3_Training_Loss.png"
    
    if not csv_path.exists():
        print(f"Error: CSV log not found at {csv_path}")
        sys.exit(1)
        
    df = pd.read_csv(csv_path)
    
    # Extract only B3 data (last 30 epochs assuming 30 for B0 and 30 for B3)
    # To be safe, if there are exactly 60 rows, grab the last 30.
    if len(df) >= 30:
        df_b3 = df.iloc[-30:].copy()
    else:
        df_b3 = df.copy()
        
    df_b3.reset_index(drop=True, inplace=True)
    epochs = range(1, len(df_b3) + 1)
    
    # Find fine-tuning marker based on learning rate drop
    # Stage 1 was 1e-4, Stage 2 was 1e-5.
    stage2_start = None
    for i, lr in enumerate(df_b3['learning_rate']):
        if lr < 5e-5: # Dropped below 1e-4 threshold
            stage2_start = i + 1 # 1-indexed epoch
            break
            
    if stage2_start is None:
        stage2_start = 16 # Fallback if not found
        
    print(f"Detected Stage 2 (Fine-tuning) start at Epoch {stage2_start}")
    
    # --- Plot Accuracy ---
    plt.figure(figsize=(10, 6))
    plt.plot(epochs, df_b3['accuracy'], 'b-', label='Training Accuracy', linewidth=2.5)
    plt.plot(epochs, df_b3['val_accuracy'], 'r-', label='Validation Accuracy', linewidth=2.5)
    
    plt.axvline(x=stage2_start, color='green', linestyle='--', alpha=0.7, label='Stage 2 (Fine-tuning)', linewidth=2)
    
    plt.title('EfficientNetB3 - Training and Validation Accuracy', fontsize=16, fontweight='bold', pad=15)
    plt.xlabel('Epochs', fontsize=14)
    plt.ylabel('Accuracy', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(fontsize=12, loc='lower right')
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_acc, dpi=300, bbox_inches='tight')
    plt.close()
    
    # --- Plot Loss ---
    plt.figure(figsize=(10, 6))
    plt.plot(epochs, df_b3['loss'], 'b-', label='Training Loss', linewidth=2.5)
    plt.plot(epochs, df_b3['val_loss'], 'r-', label='Validation Loss', linewidth=2.5)
    
    plt.axvline(x=stage2_start, color='green', linestyle='--', alpha=0.7, label='Stage 2 (Fine-tuning)', linewidth=2)
    
    plt.title('EfficientNetB3 - Training and Validation Loss', fontsize=16, fontweight='bold', pad=15)
    plt.xlabel('Epochs', fontsize=14)
    plt.ylabel('Loss', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(fontsize=12, loc='upper right')
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_loss, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Successfully generated high-resolution training graphs:")
    print(f"- {output_acc}")
    print(f"- {output_loss}")

if __name__ == "__main__":
    main()
