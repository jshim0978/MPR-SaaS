#!/usr/bin/env python3
"""
Prepare knowledge-based datasets (Wikidata, Wikipedia, KILT) for fine-tuning.
Creates a combined dataset optimized for knowledge enhancement.
"""

from datasets import load_dataset
import json
import random
import os

def prepare_wikidata_descriptions(max_samples=50000, output_dir="/home/data"):
    """
    Prepare Wikidata descriptions for entity understanding.
    Format: "What is [entity]?" -> "[description]"
    """
    print("\n" + "="*80)
    print("Preparing Wikidata Descriptions")
    print("="*80)
    
    try:
        print(f"Loading Wikidata descriptions (targeting {max_samples} samples)...")
        
        # Load with correct split
        dataset = load_dataset("masaki-sakata/wikidata_descriptions", split="en", streaming=True)
        
        examples = []
        for i, item in enumerate(dataset):
            if i >= max_samples:
                break
            
            # Extract entity and description
            entity_id = item.get('id', '')
            label = item.get('label', '')
            description = item.get('description', '')
            
            if label and description and len(description) > 20:
                # Format as Q&A
                examples.append({
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a knowledgeable assistant that provides accurate definitions and descriptions of entities."
                        },
                        {
                            "role": "user",
                            "content": f"What is {label}?"
                        },
                        {
                            "role": "assistant",
                            "content": description
                        }
                    ]
                })
            
            if (i + 1) % 10000 == 0:
                print(f"  Processed {i + 1} samples...")
        
        print(f"✅ Collected {len(examples)} Wikidata examples")
        
        # Save
        output_path = os.path.join(output_dir, "wikidata_knowledge.jsonl")
        with open(output_path, 'w', encoding='utf-8') as f:
            for example in examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        print(f"✅ Saved to {output_path}")
        return examples
        
    except Exception as e:
        print(f"❌ Error preparing Wikidata: {e}")
        return []

def prepare_wikipedia(max_samples=20000, output_dir="/home/data"):
    """
    Prepare Wikipedia articles for comprehensive knowledge.
    Format: "Tell me about [title]" -> "[text]"
    """
    print("\n" + "="*80)
    print("Preparing Wikipedia Articles")
    print("="*80)
    
    try:
        print(f"Loading Wikipedia (targeting {max_samples} articles)...")
        
        # Load English Wikipedia
        dataset = load_dataset("wikimedia/wikipedia", "20231101.en", split="train", streaming=True)
        
        examples = []
        for i, item in enumerate(dataset):
            if i >= max_samples:
                break
            
            title = item.get('title', '')
            text = item.get('text', '')
            
            # Filter: must have reasonable length and be informative
            if title and text and len(text) > 200 and len(text) < 2000:
                # Take first paragraph as summary
                first_para = text.split('\n\n')[0] if '\n\n' in text else text[:500]
                
                examples.append({
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a knowledgeable assistant that provides comprehensive information on various topics."
                        },
                        {
                            "role": "user",
                            "content": f"Tell me about {title}."
                        },
                        {
                            "role": "assistant",
                            "content": first_para
                        }
                    ]
                })
            
            if (i + 1) % 5000 == 0:
                print(f"  Processed {i + 1} articles, collected {len(examples)} suitable ones...")
        
        print(f"✅ Collected {len(examples)} Wikipedia examples")
        
        # Save
        output_path = os.path.join(output_dir, "wikipedia_knowledge.jsonl")
        with open(output_path, 'w', encoding='utf-8') as f:
            for example in examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        print(f"✅ Saved to {output_path}")
        return examples
        
    except Exception as e:
        print(f"❌ Error preparing Wikipedia: {e}")
        return []

def prepare_kilt_wow(max_samples=30000, output_dir="/home/data"):
    """
    Prepare KILT Wizard of Wikipedia for knowledge-grounded dialogue.
    Format: conversation turns with knowledge
    """
    print("\n" + "="*80)
    print("Preparing KILT (Wizard of Wikipedia)")
    print("="*80)
    
    try:
        print(f"Loading KILT WoW (targeting {max_samples} examples)...")
        
        # Load Wizard of Wikipedia from KILT
        dataset = load_dataset("facebook/kilt_tasks", "wow", split="train", streaming=True)
        
        examples = []
        for i, item in enumerate(dataset):
            if i >= max_samples:
                break
            
            # Extract input and output
            input_text = item.get('input', '')
            output = item.get('output', [])
            
            if input_text and output and len(output) > 0:
                answer = output[0].get('answer', '') if isinstance(output[0], dict) else str(output[0])
                
                if answer and len(answer) > 10:
                    examples.append({
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a knowledgeable assistant that provides informative and engaging responses based on your knowledge."
                            },
                            {
                                "role": "user",
                                "content": input_text
                            },
                            {
                                "role": "assistant",
                                "content": answer
                            }
                        ]
                    })
            
            if (i + 1) % 10000 == 0:
                print(f"  Processed {i + 1} samples...")
        
        print(f"✅ Collected {len(examples)} KILT WoW examples")
        
        # Save
        output_path = os.path.join(output_dir, "kilt_wow_knowledge.jsonl")
        with open(output_path, 'w', encoding='utf-8') as f:
            for example in examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        print(f"✅ Saved to {output_path}")
        return examples
        
    except Exception as e:
        print(f"❌ Error preparing KILT: {e}")
        return []

def combine_knowledge_datasets(output_dir="/home/data"):
    """Combine all knowledge datasets"""
    print("\n" + "="*80)
    print("Combining Knowledge Datasets")
    print("="*80)
    
    all_examples = []
    
    # Load all prepared datasets
    files = [
        "wikidata_knowledge.jsonl",
        "wikipedia_knowledge.jsonl",
        "kilt_wow_knowledge.jsonl"
    ]
    
    for filename in files:
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            print(f"Loading {filename}...")
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    all_examples.append(json.loads(line))
            print(f"  Loaded {sum(1 for _ in open(filepath))} examples")
    
    # Shuffle for better training
    random.seed(42)
    random.shuffle(all_examples)
    
    print(f"\n✅ Total examples: {len(all_examples)}")
    
    # Save combined
    output_path = os.path.join(output_dir, "knowledge_combined_train.jsonl")
    with open(output_path, 'w', encoding='utf-8') as f:
        for example in all_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    print(f"✅ Saved combined dataset to {output_path}")
    
    # Create LLaMA-Factory format
    llamafactory_path = os.path.join(output_dir, "knowledge_combined.json")
    with open(llamafactory_path, 'w', encoding='utf-8') as f:
        json.dump(all_examples, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved LLaMA-Factory format to {llamafactory_path}")
    
    return len(all_examples)

def main():
    print("🧠 Preparing Knowledge-based Datasets for Fine-tuning")
    print("="*80)
    
    os.makedirs("/home/data", exist_ok=True)
    
    # Prepare each dataset
    wikidata = prepare_wikidata_descriptions(max_samples=50000)
    wikipedia = prepare_wikipedia(max_samples=20000)
    kilt = prepare_kilt_wow(max_samples=30000)
    
    # Combine
    total = combine_knowledge_datasets()
    
    # Summary
    print("\n" + "="*80)
    print("📊 PREPARATION SUMMARY")
    print("="*80)
    print(f"Wikidata: {len(wikidata)} examples")
    print(f"Wikipedia: {len(wikipedia)} examples")
    print(f"KILT WoW: {len(kilt)} examples")
    print(f"Total Combined: {total} examples")
    print("\n✅ Knowledge datasets ready for fine-tuning!")

if __name__ == "__main__":
    main()

