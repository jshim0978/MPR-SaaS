#!/usr/bin/env python3
"""
Prepare individual knowledge datasets for single-dataset training.
Creates: wikidata_only, wikipedia_only, kilt_wow_only datasets.
"""

import json
from datasets import load_dataset
from tqdm import tqdm
import random

# Set cache
import os
os.environ['HF_HOME'] = '/home/hf_cache'

def prepare_wikidata_dataset():
    """Prepare Wikidata descriptions dataset."""
    print("\n" + "="*80)
    print("📚 PREPARING WIKIDATA DATASET")
    print("="*80)
    
    dataset = load_dataset("masaki-sakata/wikidata_descriptions", split="en", trust_remote_code=True)
    
    print(f"Total examples: {len(dataset)}")
    
    # Sample 10k examples
    random.seed(42)
    sampled = random.sample(list(dataset), min(10000, len(dataset)))
    
    data = []
    for item in tqdm(sampled, desc="Processing"):
        if item.get('description'):
            messages = [
                {"role": "user", "content": f"Define the entity: {item.get('wiki_title', 'this concept')}"},
                {"role": "assistant", "content": item['description']}
            ]
            data.append({"messages": messages})
    
    # Save
    output_file = "/home/data/wikidata_only.json"
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Saved {len(data)} examples to {output_file}")
    return len(data)

def prepare_wikipedia_dataset():
    """Prepare Wikipedia dataset."""
    print("\n" + "="*80)
    print("📚 PREPARING WIKIPEDIA DATASET")
    print("="*80)
    
    dataset = load_dataset("wikimedia/wikipedia", "20231101.en", split="train", trust_remote_code=True, streaming=True)
    
    # Take first 15k articles
    data = []
    for i, item in enumerate(tqdm(dataset, desc="Processing", total=15000)):
        if i >= 15000:
            break
        
        if item.get('text') and len(item['text']) > 100:
            # Create summarization task
            text = item['text'][:1000]  # First 1000 chars
            messages = [
                {"role": "user", "content": f"Provide information about: {item.get('title', 'this topic')}"},
                {"role": "assistant", "content": text}
            ]
            data.append({"messages": messages})
    
    # Save
    output_file = "/home/data/wikipedia_only.json"
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Saved {len(data)} examples to {output_file}")
    return len(data)

def prepare_kilt_wow_dataset():
    """Prepare KILT Wizard of Wikipedia dataset."""
    print("\n" + "="*80)
    print("📚 PREPARING KILT WOW DATASET")
    print("="*80)
    
    dataset = load_dataset("facebook/kilt_tasks", "wow", split="train", trust_remote_code=True)
    
    print(f"Total examples: {len(dataset)}")
    
    # Sample 15k examples
    random.seed(42)
    sampled = random.sample(list(dataset), min(15000, len(dataset)))
    
    data = []
    for item in tqdm(sampled, desc="Processing"):
        if item.get('output') and len(item['output']) > 0:
            # Use the knowledge-grounded dialogue
            output_text = item['output'][0].get('answer', '') if item['output'] else ''
            if output_text:
                messages = [
                    {"role": "user", "content": item.get('input', 'Provide information.')},
                    {"role": "assistant", "content": output_text}
                ]
                data.append({"messages": messages})
    
    # Save
    output_file = "/home/data/kilt_wow_only.json"
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Saved {len(data)} examples to {output_file}")
    return len(data)

def main():
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║        PREPARING INDIVIDUAL KNOWLEDGE DATASETS                           ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print()
    print("This script will create three individual datasets:")
    print("  1. Wikidata-only (~10k examples)")
    print("  2. Wikipedia-only (~15k examples)")
    print("  3. KILT WOW-only (~15k examples)")
    print()
    
    # Prepare each dataset
    wikidata_count = prepare_wikidata_dataset()
    wikipedia_count = prepare_wikipedia_dataset()
    kilt_count = prepare_kilt_wow_dataset()
    
    print("\n" + "="*80)
    print("✅ ALL DATASETS PREPARED")
    print("="*80)
    print(f"  • Wikidata:   {wikidata_count:,} examples")
    print(f"  • Wikipedia:  {wikipedia_count:,} examples")
    print(f"  • KILT WOW:   {kilt_count:,} examples")
    print(f"  • Total:      {wikidata_count + wikipedia_count + kilt_count:,} examples")
    print()
    print("Next steps:")
    print("  1. Update dataset_info.json with new datasets")
    print("  2. Create training configs for each dataset")
    print("  3. Run training for 3B and 8B models")
    print()

if __name__ == "__main__":
    main()

