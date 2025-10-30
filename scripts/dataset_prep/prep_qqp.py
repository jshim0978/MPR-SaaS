#!/usr/bin/env python3
"""
Prepare QQP (Quora Question Pairs) dataset for paraphrasing fine-tuning.
Uses bidirectional generation: each positive pair creates 2 training examples.
"""

from datasets import load_dataset
import json
import os

def prepare_qqp_for_paraphrasing(output_dir="/home/data", max_train_samples=50000):
    """
    Download and prepare QQP dataset for paraphrasing fine-tuning.
    Only uses positive pairs (is_duplicate=1) and creates bidirectional examples.
    
    Args:
        max_train_samples: Maximum number of positive pairs to use for training
                          (QQP is very large, so we limit it for balance)
    """
    
    print("="*80)
    print("Preparing QQP Dataset for Paraphrasing Fine-tuning")
    print("="*80)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Load QQP dataset
    print("\n📦 Loading QQP dataset...")
    try:
        dataset = load_dataset("AlekseyKorshuk/quora-question-pairs")
    except Exception as e:
        print(f"❌ Error loading QQP dataset: {e}")
        print("Trying alternative loading method...")
        dataset = load_dataset("quora")
    
    print(f"✅ Loaded QQP dataset:")
    print(f"   Train: {len(dataset['train'])} examples")
    
    def process_split(split_name, split_data, max_positive=None):
        """Process a single split and create bidirectional examples"""
        examples = []
        positive_count = 0
        skipped_count = 0
        
        for item in split_data:
            # Skip if we've reached max_positive limit
            if max_positive and positive_count >= max_positive:
                break
            
            # Check for duplicate/paraphrase label (field name may vary)
            is_duplicate = item.get('is_duplicate', item.get('label', 0))
            
            # Only use positive pairs (duplicates/paraphrases)
            if is_duplicate == 1:
                question1 = item.get('question1', item.get('questions', {}).get('text', [''])[0])
                question2 = item.get('question2', item.get('questions', {}).get('text', ['', ''])[1])
                
                # Skip if either question is empty or too short
                if not question1 or not question2 or len(question1.strip()) < 10 or len(question2.strip()) < 10:
                    skipped_count += 1
                    continue
                
                question1 = question1.strip()
                question2 = question2.strip()
                
                positive_count += 1
                
                # Create bidirectional examples
                # Direction 1: question1 -> question2
                examples.append({
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that paraphrases text while preserving the original meaning."
                        },
                        {
                            "role": "user",
                            "content": f"Paraphrase this: {question1}"
                        },
                        {
                            "role": "assistant",
                            "content": question2
                        }
                    ]
                })
                
                # Direction 2: question2 -> question1
                examples.append({
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that paraphrases text while preserving the original meaning."
                        },
                        {
                            "role": "user",
                            "content": f"Paraphrase this: {question2}"
                        },
                        {
                            "role": "assistant",
                            "content": question1
                        }
                    ]
                })
        
        print(f"   {split_name}: {positive_count} positive pairs → {len(examples)} bidirectional examples")
        if skipped_count > 0:
            print(f"   (Skipped {skipped_count} pairs with empty/short questions)")
        return examples, positive_count
    
    # Process train split with limit
    print(f"\n🔄 Processing train split (limiting to {max_train_samples} positive pairs)...")
    
    train_examples, train_positive = process_split("train", dataset['train'], max_positive=max_train_samples)
    
    # Save to JSONL file
    print("\n💾 Saving processed data...")
    
    train_path = os.path.join(output_dir, "qqp_paraphrase_train.jsonl")
    with open(train_path, 'w', encoding='utf-8') as f:
        for example in train_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    print(f"   ✅ Saved {len(train_examples)} examples to {train_path}")
    
    # Statistics
    print("\n" + "="*80)
    print("📊 QQP Dataset Statistics")
    print("="*80)
    print(f"Original positive pairs:")
    print(f"   Train: {train_positive}")
    print(f"\nBidirectional training examples (2x):")
    print(f"   Train: {len(train_examples)}")
    print("="*80)
    
    return {
        'train': len(train_examples)
    }

if __name__ == "__main__":
    stats = prepare_qqp_for_paraphrasing()
    print("\n✅ QQP dataset preparation complete!")

