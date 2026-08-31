import os
import json
import shutil
import random
from pathlib import Path
import argparse

def split_dataset(audit_report_path, output_dir, seed=42, train_ratio=0.7, val_ratio=0.15):
    random.seed(seed)
    
    with open(audit_report_path, 'r') as f:
        audit_data = json.load(f)
        
    dataset_root = Path(audit_data["dataset_root"])
    classes = audit_data["classes"]
    
    # 1. Identify files to ignore
    files_to_ignore = set()
    
    # Ignore cross-class leakage entirely
    for conflict in audit_data["duplicates_across_classes"]:
        for file_path in conflict["files"]:
            files_to_ignore.add(file_path)
            
    # For same-class duplicates, keep the first one, ignore the rest
    for dup_group in audit_data["duplicates_within_class"]:
        # dup_group is a list of paths
        for file_path in dup_group[1:]:
            files_to_ignore.add(file_path)
            
    print(f"Total duplicate/conflict files to ignore: {len(files_to_ignore)}")
    
    # 2. Gather unique clean files per class
    clean_files_per_class = {c: [] for c in classes}
    
    for c in classes:
        cls_dir = dataset_root / c
        for root, _, files in os.walk(cls_dir):
            for file in files:
                file_path = str(Path(root) / file)
                if file_path not in files_to_ignore:
                    clean_files_per_class[c].append(file_path)
                    
    # 3. Create splits
    out_path = Path(output_dir)
    for split in ['train', 'val', 'test']:
        for c in classes:
            (out_path / split / c).mkdir(parents=True, exist_ok=True)
            
    print("\nSplitting and copying files...")
    split_counts = {"train": 0, "val": 0, "test": 0}
    
    for c in classes:
        files = clean_files_per_class[c]
        # Sort to ensure reproducibility before shuffling
        files.sort()
        random.shuffle(files)
        
        total = len(files)
        train_end = int(total * train_ratio)
        val_end = train_end + int(total * val_ratio)
        
        train_files = files[:train_end]
        val_files = files[train_end:val_end]
        test_files = files[val_end:]
        
        splits = {
            "train": train_files,
            "val": val_files,
            "test": test_files
        }
        
        for split_name, split_list in splits.items():
            split_counts[split_name] += len(split_list)
            for file_path in split_list:
                src = file_path
                dst = out_path / split_name / c / Path(file_path).name
                shutil.copy2(src, dst)
                
    print("\nDataset split complete!")
    print(f"Train: {split_counts['train']} images")
    print(f"Validation: {split_counts['val']} images")
    print(f"Test: {split_counts['test']} images")
    print(f"Total Clean Images: {sum(split_counts.values())}")
    
    # Save the distribution for reference
    distribution = {
        "train": split_counts["train"],
        "val": split_counts["val"],
        "test": split_counts["test"],
        "total": sum(split_counts.values()),
        "seed": seed
    }
    
    with open(out_path / "split_info.json", "w") as f:
        json.dump(distribution, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split StellarX dataset")
    parser.add_argument("--audit-report", type=str, required=True, help="Path to audit JSON")
    parser.add_argument("--output-dir", type=str, required=True, help="Path to save processed data")
    
    args = parser.parse_args()
    split_dataset(args.audit_report, args.output_dir)
