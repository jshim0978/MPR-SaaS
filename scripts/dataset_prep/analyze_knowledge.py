#!/usr/bin/env python3
"""
Analyze Wikidata, Wikipedia, and KILT datasets for knowledge-based fine-tuning.
Determines optimal sampling strategy and prepares combined dataset.
"""

from datasets import load_dataset
import json
import os
from collections import Counter

def analyze_dataset(dataset_name, config=None, split='train', sample_size=1000):
    """Analyze a dataset to understand its structure and size"""
    print(f"\n{'='*80}")
    print(f"Analyzing: {dataset_name}" + (f" ({config})" if config else ""))
    print(f"{'='*80}")
    
    try:
        # Load dataset
        print(f"Loading {sample_size} samples for analysis...")
        if config:
            dataset = load_dataset(dataset_name, config, split=split, streaming=True)
        else:
            dataset = load_dataset(dataset_name, split=split, streaming=True)
        
        # Analyze samples
        samples = []
        field_types = {}
        total_chars = 0
        
        for i, sample in enumerate(dataset):
            if i >= sample_size:
                break
            samples.append(sample)
            
            # Track field types
            for key, value in sample.items():
                if key not in field_types:
                    field_types[key] = type(value).__name__
                if isinstance(value, str):
                    total_chars += len(value)
        
        # Print analysis
        print(f"\n✅ Successfully loaded {len(samples)} samples")
        print(f"\nFields: {list(field_types.keys())}")
        print(f"Field types: {field_types}")
        print(f"Avg chars per sample: {total_chars // len(samples) if samples else 0}")
        
        # Show example
        if samples:
            print(f"\n📝 Example sample:")
            example = samples[0]
            for key, value in example.items():
                if isinstance(value, str):
                    preview = value[:200] + "..." if len(value) > 200 else value
                    print(f"  {key}: {preview}")
                else:
                    print(f"  {key}: {value}")
        
        return {
            'name': dataset_name,
            'config': config,
            'samples_analyzed': len(samples),
            'fields': field_types,
            'avg_chars': total_chars // len(samples) if samples else 0,
            'example': samples[0] if samples else None
        }
        
    except Exception as e:
        print(f"❌ Error analyzing {dataset_name}: {e}")
        return None

def main():
    print("🔍 Analyzing Knowledge-based Datasets for Fine-tuning")
    print("="*80)
    
    datasets_to_analyze = [
        ("masaki-sakata/wikidata_descriptions", None),
        ("wikimedia/wikipedia", "20231101.en"),  # English Wikipedia
        ("facebook/kilt_tasks", "wow"),  # Wizard of Wikipedia subset
    ]
    
    results = []
    
    for dataset_name, config in datasets_to_analyze:
        result = analyze_dataset(dataset_name, config, sample_size=1000)
        if result:
            results.append(result)
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 ANALYSIS SUMMARY")
    print(f"{'='*80}")
    
    for result in results:
        print(f"\nDataset: {result['name']}")
        if result['config']:
            print(f"  Config: {result['config']}")
        print(f"  Fields: {', '.join(result['fields'].keys())}")
        print(f"  Avg chars: {result['avg_chars']}")
    
    # Recommendations
    print(f"\n{'='*80}")
    print("💡 RECOMMENDATIONS")
    print(f"{'='*80}")
    
    print("""
Based on analysis, here's the optimal strategy:

1. **Wikidata Descriptions**: Entity descriptions (ID → text)
   - Use for: Entity understanding, definition generation
   - Sample: 50k examples
   
2. **Wikipedia**: Full articles 
   - Use for: Comprehensive knowledge, context understanding
   - Sample: 20k articles (too large otherwise)
   
3. **KILT (Wizard of Wikipedia)**: Knowledge-grounded dialogues
   - Use for: Conversational knowledge application
   - Sample: 30k examples

**Total Combined**: ~100k examples
**Training Format**: Question-Answer or Description-Generation
**Expected Training Time**: ~6-8 hours per model
    """)
    
    # Save results
    with open("/home/knowledge_dataset_analysis.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n✅ Analysis saved to: /home/knowledge_dataset_analysis.json")

if __name__ == "__main__":
    main()

