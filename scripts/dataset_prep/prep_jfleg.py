#!/usr/bin/env python3
"""
JFLEG Dataset Preparation with All Corrections
Uses all 4 human corrections per example for maximum training data diversity
"""

import json
import random
from datasets import load_dataset

def prepare_jfleg_with_all_corrections():
    """Load JFLEG dataset and use all corrections as separate training examples"""
    print("Loading JFLEG dataset...")
    dataset = load_dataset('jhu-clsp/jfleg')
    
    print(f"Original splits: {list(dataset.keys())}")
    print(f"Validation: {len(dataset['validation'])} examples")
    print(f"Test: {len(dataset['test'])} examples")
    
    # Combine all examples
    all_examples = []
    
    # Add validation examples
    for example in dataset['validation']:
        all_examples.append(example)
    
    # Add test examples  
    for example in dataset['test']:
        all_examples.append(example)
    
    print(f"Total original examples: {len(all_examples)}")
    
    # Expand with all corrections
    expanded_examples = []
    
    for example in all_examples:
        sentence = example['sentence']
        corrections = example['corrections']
        
        # Create a separate example for each correction
        for correction in corrections:
            expanded_examples.append({
                'sentence': sentence,
                'correction': correction
            })
    
    print(f"Total expanded examples: {len(expanded_examples)}")
    
    # Shuffle and split
    random.seed(42)
    random.shuffle(expanded_examples)
    
    train_size = int(0.8 * len(expanded_examples))
    val_size = int(0.1 * len(expanded_examples))
    
    train_examples = expanded_examples[:train_size]
    val_examples = expanded_examples[train_size:train_size + val_size]
    test_examples = expanded_examples[train_size + val_size:]
    
    print(f"Train: {len(train_examples)} examples")
    print(f"Validation: {len(val_examples)} examples") 
    print(f"Test: {len(test_examples)} examples")
    
    return train_examples, val_examples, test_examples

def create_chat_format(sentence, correction):
    """Create chat format for Llama training"""
    return {
        "messages": [
            {
                "role": "user", 
                "content": f"Fix the grammar and spelling:\n{sentence}"
            },
            {
                "role": "assistant", 
                "content": correction
            }
        ]
    }

def save_jsonl(data, filename):
    """Save data to JSONL file"""
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"Saved {len(data)} examples to {filename}")

def main():
    print("Preparing JFLEG Dataset with All Corrections")
    print("=" * 60)
    
    # Prepare dataset
    train_examples, val_examples, test_examples = prepare_jfleg_with_all_corrections()
    
    # Convert to chat format
    print("\nConverting to chat format...")
    
    train_chat = []
    for example in train_examples:
        chat_format = create_chat_format(example['sentence'], example['correction'])
        train_chat.append(chat_format)
    
    val_chat = []
    for example in val_examples:
        chat_format = create_chat_format(example['sentence'], example['correction'])
        val_chat.append(chat_format)
    
    test_chat = []
    for example in test_examples:
        chat_format = create_chat_format(example['sentence'], example['correction'])
        test_chat.append(chat_format)
    
    # Save files
    print("\nSaving files...")
    save_jsonl(train_chat, "/home/data/jfleg_all_corrections_train.jsonl")
    save_jsonl(val_chat, "/home/data/jfleg_all_corrections_eval.jsonl")
    save_jsonl(test_chat, "/home/data/jfleg_all_corrections_test.jsonl")
    
    print("\n✅ JFLEG dataset with all corrections preparation complete!")
    print("Files saved:")
    print("- /home/data/jfleg_all_corrections_train.jsonl")
    print("- /home/data/jfleg_all_corrections_eval.jsonl") 
    print("- /home/data/jfleg_all_corrections_test.jsonl")
    
    print(f"\n📊 Dataset Statistics:")
    print(f"- Training examples: {len(train_chat):,}")
    print(f"- Validation examples: {len(val_chat):,}")
    print(f"- Test examples: {len(test_chat):,}")
    print(f"- Total examples: {len(train_chat) + len(val_chat) + len(test_chat):,}")

if __name__ == "__main__":
    main()
