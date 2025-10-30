#!/usr/bin/env python3
"""
Prepare PAWS dataset for paraphrasing fine-tuning.
Uses bidirectional generation: each positive pair creates 2 training examples.
"""

from datasets import load_dataset
import json
import os

def prepare_paws_for_paraphrasing(output_dir="/home/data"):
    """
    Download and prepare PAWS dataset for paraphrasing fine-tuning.
    Only uses positive pairs (label=1) and creates bidirectional examples.
    """
    
    print("="*80)
    print("Preparing PAWS Dataset for Paraphrasing Fine-tuning")
    print("="*80)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Load PAWS labeled_final subset (highest quality)
    print("\n📦 Loading PAWS dataset (labeled_final)...")
    dataset = load_dataset("google-research-datasets/paws", "labeled_final")
    
    print(f"✅ Loaded PAWS dataset:")
    print(f"   Train: {len(dataset['train'])} examples")
    print(f"   Validation: {len(dataset['validation'])} examples")
    print(f"   Test: {len(dataset['test'])} examples")
    
    def process_split(split_name, split_data):
        """Process a single split and create bidirectional examples"""
        examples = []
        positive_count = 0
        
        for item in split_data:
            # Only use positive pairs (paraphrases)
            if item['label'] == 1:
                positive_count += 1
                sentence1 = item['sentence1'].strip()
                sentence2 = item['sentence2'].strip()
                
                # Create bidirectional examples
                # Direction 1: sentence1 -> sentence2
                examples.append({
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that paraphrases text while preserving the original meaning."
                        },
                        {
                            "role": "user",
                            "content": f"Paraphrase this: {sentence1}"
                        },
                        {
                            "role": "assistant",
                            "content": sentence2
                        }
                    ]
                })
                
                # Direction 2: sentence2 -> sentence1
                examples.append({
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that paraphrases text while preserving the original meaning."
                        },
                        {
                            "role": "user",
                            "content": f"Paraphrase this: {sentence2}"
                        },
                        {
                            "role": "assistant",
                            "content": sentence1
                        }
                    ]
                })
        
        print(f"   {split_name}: {positive_count} positive pairs → {len(examples)} bidirectional examples")
        return examples, positive_count
    
    # Process each split
    print("\n🔄 Processing splits (filtering positive pairs only)...")
    
    train_examples, train_positive = process_split("train", dataset['train'])
    val_examples, val_positive = process_split("validation", dataset['validation'])
    test_examples, test_positive = process_split("test", dataset['test'])
    
    # Save to JSONL files
    print("\n💾 Saving processed data...")
    
    splits = {
        "train": (train_examples, "paws_paraphrase_train.jsonl"),
        "validation": (val_examples, "paws_paraphrase_eval.jsonl"),
        "test": (test_examples, "paws_paraphrase_test.jsonl")
    }
    
    for split_name, (examples, filename) in splits.items():
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            for example in examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        print(f"   ✅ Saved {len(examples)} examples to {output_path}")
    
    # Statistics
    print("\n" + "="*80)
    print("📊 PAWS Dataset Statistics")
    print("="*80)
    print(f"Original positive pairs:")
    print(f"   Train: {train_positive}")
    print(f"   Validation: {val_positive}")
    print(f"   Test: {test_positive}")
    print(f"   Total: {train_positive + val_positive + test_positive}")
    print(f"\nBidirectional training examples (2x):")
    print(f"   Train: {len(train_examples)}")
    print(f"   Validation: {len(val_examples)}")
    print(f"   Test: {len(test_examples)}")
    print(f"   Total: {len(train_examples) + len(val_examples) + len(test_examples)}")
    print("="*80)
    
    return {
        'train': len(train_examples),
        'validation': len(val_examples),
        'test': len(test_examples)
    }

if __name__ == "__main__":
    stats = prepare_paws_for_paraphrasing()
    print("\n✅ PAWS dataset preparation complete!")

