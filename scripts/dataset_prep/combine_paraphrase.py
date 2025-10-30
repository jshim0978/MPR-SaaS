#!/usr/bin/env python3
"""
Combine PAWS and QQP datasets into a single paraphrasing training dataset.
"""

import json
import random
import os

def combine_paraphrase_datasets(output_dir="/home/data"):
    """
    Combine PAWS and QQP datasets into a unified paraphrasing dataset.
    """
    
    print("="*80)
    print("Combining PAWS and QQP Datasets")
    print("="*80)
    
    # File paths
    paws_train = os.path.join(output_dir, "paws_paraphrase_train.jsonl")
    paws_eval = os.path.join(output_dir, "paws_paraphrase_eval.jsonl")
    paws_test = os.path.join(output_dir, "paws_paraphrase_test.jsonl")
    qqp_train = os.path.join(output_dir, "qqp_paraphrase_train.jsonl")
    
    # Load datasets
    print("\n📂 Loading prepared datasets...")
    
    def load_jsonl(filepath):
        """Load JSONL file"""
        if not os.path.exists(filepath):
            print(f"   ⚠️  File not found: {filepath}")
            return []
        examples = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                examples.append(json.loads(line))
        print(f"   ✅ Loaded {len(examples)} examples from {os.path.basename(filepath)}")
        return examples
    
    paws_train_data = load_jsonl(paws_train)
    paws_eval_data = load_jsonl(paws_eval)
    paws_test_data = load_jsonl(paws_test)
    qqp_train_data = load_jsonl(qqp_train)
    
    # Combine training data
    print("\n🔀 Combining training data...")
    combined_train = paws_train_data + qqp_train_data
    
    # Shuffle combined training data
    random.seed(42)
    random.shuffle(combined_train)
    
    print(f"   Combined training examples: {len(combined_train)}")
    print(f"   - From PAWS: {len(paws_train_data)}")
    print(f"   - From QQP: {len(qqp_train_data)}")
    
    # Save combined datasets
    print("\n💾 Saving combined datasets...")
    
    # Save combined training data
    combined_train_path = os.path.join(output_dir, "paraphrase_combined_train.jsonl")
    with open(combined_train_path, 'w', encoding='utf-8') as f:
        for example in combined_train:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    print(f"   ✅ Saved {len(combined_train)} training examples to {combined_train_path}")
    
    # Use PAWS validation/test as they are higher quality
    combined_eval_path = os.path.join(output_dir, "paraphrase_combined_eval.jsonl")
    with open(combined_eval_path, 'w', encoding='utf-8') as f:
        for example in paws_eval_data:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    print(f"   ✅ Saved {len(paws_eval_data)} validation examples to {combined_eval_path}")
    
    combined_test_path = os.path.join(output_dir, "paraphrase_combined_test.jsonl")
    with open(combined_test_path, 'w', encoding='utf-8') as f:
        for example in paws_test_data:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    print(f"   ✅ Saved {len(paws_test_data)} test examples to {combined_test_path}")
    
    # Create LLaMA-Factory compatible JSON format
    print("\n📦 Creating LLaMA-Factory dataset format...")
    
    combined_data = []
    
    # Add all splits
    for example in combined_train + paws_eval_data:
        combined_data.append({
            "messages": example["messages"]
        })
    
    llamafactory_path = os.path.join(output_dir, "paraphrase_combined.json")
    with open(llamafactory_path, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)
    print(f"   ✅ Saved {len(combined_data)} examples to {llamafactory_path}")
    
    # Statistics
    print("\n" + "="*80)
    print("📊 Combined Dataset Statistics")
    print("="*80)
    print(f"Training examples: {len(combined_train)}")
    print(f"  - PAWS contribution: {len(paws_train_data)} ({len(paws_train_data)/len(combined_train)*100:.1f}%)")
    print(f"  - QQP contribution: {len(qqp_train_data)} ({len(qqp_train_data)/len(combined_train)*100:.1f}%)")
    print(f"Validation examples: {len(paws_eval_data)} (PAWS only)")
    print(f"Test examples: {len(paws_test_data)} (PAWS only)")
    print(f"\nTotal for training: {len(combined_data)} (train + eval)")
    print("="*80)
    
    return {
        'train': len(combined_train),
        'eval': len(paws_eval_data),
        'test': len(paws_test_data),
        'total': len(combined_data)
    }

if __name__ == "__main__":
    stats = combine_paraphrase_datasets()
    print("\n✅ Dataset combination complete!")
    print(f"\n📁 Output files:")
    print(f"   - /home/data/paraphrase_combined_train.jsonl")
    print(f"   - /home/data/paraphrase_combined_eval.jsonl")
    print(f"   - /home/data/paraphrase_combined_test.jsonl")
    print(f"   - /home/data/paraphrase_combined.json (for LLaMA-Factory)")

