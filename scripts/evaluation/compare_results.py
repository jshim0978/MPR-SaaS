#!/usr/bin/env python3
"""
Display and compare evaluation results in a readable format.
"""

import json
from typing import Dict, List

def print_section_header(title: str):
    """Print a formatted section header."""
    print("\n" + "="*100)
    print(f"  {title}")
    print("="*100)

def print_comparison(results: List[Dict], task_name: str):
    """Print side-by-side comparison of model outputs."""
    
    print_section_header(f"{task_name} COMPARISON")
    
    num_samples = len(results[0]['results'])
    
    for sample_idx in range(num_samples):
        print(f"\n{'─'*100}")
        print(f"📝 Sample {sample_idx + 1}/{num_samples}")
        print(f"{'─'*100}")
        
        # Print input
        input_text = results[0]['results'][sample_idx]['input']
        print(f"\n🔹 INPUT:\n   {input_text}")
        
        # Print reference if available
        if 'reference' in results[0]['results'][sample_idx]:
            ref = results[0]['results'][sample_idx]['reference']
            print(f"\n🔹 REFERENCE:\n   {ref}")
        elif 'references' in results[0]['results'][sample_idx]:
            refs = results[0]['results'][sample_idx]['references']
            print(f"\n🔹 REFERENCES:")
            for i, ref in enumerate(refs[:3], 1):  # Show first 3
                print(f"   {i}. {ref}")
        
        # Print each model's output
        for model_result in results:
            model_name = model_result['model']
            output = model_result['results'][sample_idx]['output']
            
            # Truncate if too long
            if len(output) > 300:
                output = output[:300] + "..."
            
            print(f"\n🤖 {model_name}:")
            print(f"   {output}")
        
        print()

def print_statistics(results: List[Dict]):
    """Print basic statistics about the outputs."""
    print_section_header("OUTPUT STATISTICS")
    
    for model_result in results:
        model_name = model_result['model']
        outputs = [r['output'] for r in model_result['results']]
        
        avg_length = sum(len(o) for o in outputs) / len(outputs)
        min_length = min(len(o) for o in outputs)
        max_length = max(len(o) for o in outputs)
        
        print(f"\n📊 {model_name}:")
        print(f"   Average length: {avg_length:.1f} chars")
        print(f"   Min length: {min_length} chars")
        print(f"   Max length: {max_length} chars")

def main():
    print("="*100)
    print("  🔍 MODEL EVALUATION RESULTS COMPARISON")
    print("="*100)
    
    # Load grammar results
    try:
        print("\n\n")
        print("█"*100)
        print("  📝 GRAMMAR CORRECTION (JFLEG)")
        print("█"*100)
        
        with open("/home/evaluation_results_grammar.json", "r") as f:
            grammar_results = json.load(f)
        print_comparison(grammar_results, "GRAMMAR")
        print_statistics(grammar_results)
    except FileNotFoundError:
        print("\n⚠️  Grammar results not found")
    
    # Load paraphrase results
    try:
        print("\n\n")
        print("█"*100)
        print("  🔄 PARAPHRASING (PAWS)")
        print("█"*100)
        
        with open("/home/evaluation_results_paraphrase.json", "r") as f:
            paraphrase_results = json.load(f)
        print_comparison(paraphrase_results, "PARAPHRASE")
        print_statistics(paraphrase_results)
    except FileNotFoundError:
        print("\n⚠️  Paraphrase results not found")
    
    # Load knowledge results
    try:
        print("\n\n")
        print("█"*100)
        print("  🧠 KNOWLEDGE (Wizard of Wikipedia)")
        print("█"*100)
        
        with open("/home/evaluation_results_knowledge.json", "r") as f:
            knowledge_results = json.load(f)
        print_comparison(knowledge_results, "KNOWLEDGE")
        print_statistics(knowledge_results)
    except FileNotFoundError:
        print("\n⚠️  Knowledge results not found")
    
    print("\n\n")
    print("="*100)
    print("  ✅ COMPARISON COMPLETE")
    print("="*100)
    print("\n💡 TIP: Review the outputs to assess:")
    print("   • Grammar: Correctness and fluency")
    print("   • Paraphrase: Semantic preservation and diversity")
    print("   • Knowledge: Factual accuracy and detail")
    print()

if __name__ == "__main__":
    main()

