import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys

def create_plot(df, title_prefix, output_acc, output_loss):
    epochs = range(1, len(df) + 1)
    
    # Plot Accuracy
    plt.figure(figsize=(10, 6))
    plt.plot(epochs, df['accuracy'], 'b-', label='Training Accuracy', linewidth=2)
    plt.plot(epochs, df['val_accuracy'], 'r-', label='Validation Accuracy', linewidth=2)
    plt.title(f'{title_prefix} - Training and Validation Accuracy', fontsize=14)
    plt.xlabel('Epochs', fontsize=12)
    plt.ylabel('Accuracy', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    
    if len(df) >= 15:
        plt.axvline(x=15, color='green', linestyle='--', alpha=0.5, label='Stage 2 (Fine-tuning)')
        plt.legend()
        
    plt.tight_layout()
    plt.savefig(output_acc, dpi=300)
    plt.close()
    
    # Plot Loss
    plt.figure(figsize=(10, 6))
    plt.plot(epochs, df['loss'], 'b-', label='Training Loss', linewidth=2)
    plt.plot(epochs, df['val_loss'], 'r-', label='Validation Loss', linewidth=2)
    plt.title(f'{title_prefix} - Training and Validation Loss', fontsize=14)
    plt.xlabel('Epochs', fontsize=12)
    plt.ylabel('Loss', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    
    if len(df) >= 15:
        plt.axvline(x=15, color='green', linestyle='--', alpha=0.5, label='Stage 2 (Fine-tuning)')
        plt.legend()
        
    plt.tight_layout()
    plt.savefig(output_loss, dpi=300)
    plt.close()

def main():
    workspace_dir = Path(__file__).resolve().parent.parent
    csv_path = workspace_dir / "artifacts" / "metrics" / "training_history.csv"
    
    if not csv_path.exists():
        print(f"Error: CSV log not found at {csv_path}")
        sys.exit(1)
        
    # We know that the CSV contains 60 epochs total (30 for B0, 30 for B3) 
    # because the CSVLogger appends to the same file.
    df = pd.read_csv(csv_path)
    
    if len(df) == 60:
        df_b0 = df.iloc[:30].copy()
        df_b3 = df.iloc[30:].copy()
        
        # Generate B0 plots
        create_plot(
            df_b0, 
            "EfficientNetB0", 
            workspace_dir / "artifacts" / "metrics" / "B0_accuracy_graph.png",
            workspace_dir / "artifacts" / "metrics" / "B0_loss_graph.png"
        )
        
        # Generate B3 plots
        create_plot(
            df_b3, 
            "EfficientNetB3", 
            workspace_dir / "artifacts" / "metrics" / "B3_accuracy_graph.png",
            workspace_dir / "artifacts" / "metrics" / "B3_loss_graph.png"
        )
        print("Successfully generated graphs for BOTH EfficientNetB0 and EfficientNetB3.")
    else:
        # Fallback if the CSV has a different length
        create_plot(
            df, 
            "Model", 
            workspace_dir / "artifacts" / "metrics" / "accuracy_graph.png",
            workspace_dir / "artifacts" / "metrics" / "loss_graph.png"
        )
        print("Successfully generated standard graphs.")

if __name__ == "__main__":
    main()
