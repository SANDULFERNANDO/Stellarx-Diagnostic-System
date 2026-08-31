import os
import hashlib
import json
from pathlib import Path
from collections import defaultdict
from PIL import Image, UnidentifiedImageError
import argparse

def compute_md5(file_path, chunk_size=8192):
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        return None

def run_audit(dataset_root, output_json_path):
    root_path = Path(dataset_root)
    
    classes = [d for d in os.listdir(root_path) 
               if (root_path / d).is_dir() 
               and d.lower() not in ['.git', 'doc', 'stellarx-diagnostic-system', 'stellarx_code_recovery']]
    
    audit_results = {
        "dataset_root": str(root_path),
        "classes": classes,
        "total_images": 0,
        "images_per_class": defaultdict(int),
        "extensions": defaultdict(int),
        "modes": defaultdict(int),
        "corrupted_files": [],
        "hash_registry": {}, # hash -> list of file paths
        "duplicates_within_class": [],
        "duplicates_across_classes": []
    }
    
    print(f"Starting audit on: {dataset_root}")
    print(f"Classes found: {classes}")
    
    for cls in classes:
        cls_dir = root_path / cls
        for root, _, files in os.walk(cls_dir):
            for file in files:
                file_path = Path(root) / file
                
                # Update basic counts
                audit_results["total_images"] += 1
                audit_results["images_per_class"][cls] += 1
                audit_results["extensions"][file_path.suffix.lower()] += 1
                
                # Check for corruption and read metadata
                try:
                    with Image.open(file_path) as img:
                        img.verify() # Fast check
                        audit_results["modes"][img.mode] += 1
                except (UnidentifiedImageError, OSError, SyntaxError) as e:
                    audit_results["corrupted_files"].append(str(file_path))
                    continue # Skip hash if corrupted
                
                # Compute hash for duplicates
                file_hash = compute_md5(file_path)
                if file_hash:
                    if file_hash not in audit_results["hash_registry"]:
                        audit_results["hash_registry"][file_hash] = []
                    audit_results["hash_registry"][file_hash].append((cls, str(file_path)))

    # Process duplicates
    print("\nAnalyzing exact duplicates...")
    for file_hash, occurrences in audit_results["hash_registry"].items():
        if len(occurrences) > 1:
            classes_involved = {occ[0] for occ in occurrences}
            paths = [occ[1] for occ in occurrences]
            if len(classes_involved) == 1:
                audit_results["duplicates_within_class"].append(paths)
            else:
                audit_results["duplicates_across_classes"].append({
                    "classes": list(classes_involved),
                    "files": paths
                })

    # Clean up large hash registry from final report
    del audit_results["hash_registry"]
    
    # Convert defaultdicts to dicts for JSON serialization
    audit_results["images_per_class"] = dict(audit_results["images_per_class"])
    audit_results["extensions"] = dict(audit_results["extensions"])
    audit_results["modes"] = dict(audit_results["modes"])
    
    print("\nAudit complete. Summary:")
    print(f"Total Images: {audit_results['total_images']}")
    print(f"Corrupted: {len(audit_results['corrupted_files'])}")
    print(f"Duplicates (Same Class): {len(audit_results['duplicates_within_class'])}")
    print(f"Duplicates (Cross-Class leakage): {len(audit_results['duplicates_across_classes'])}")
    
    # Save report
    out_path = Path(output_json_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(audit_results, f, indent=4)
        
    print(f"\nReport saved to {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit StellarX dataset")
    parser.add_argument("--data-root", type=str, required=True, help="Path to raw dataset")
    parser.add_argument("--output", type=str, required=True, help="Path to save JSON report")
    
    args = parser.parse_args()
    run_audit(args.data_root, args.output)
