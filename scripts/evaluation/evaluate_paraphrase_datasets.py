#!/usr/bin/env python3
"""
Comprehensive paraphrase dataset comparison evaluation.
Compares: Original vs PAWS-only vs QQP-only vs Combined for both 3B and 8B models.
"""

import os
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from datasets import load_dataset
from tqdm import tqdm
import random

# Set environment
os.environ['HF_HOME'] = '/home/hf_cache'
os.environ['TRANSFORMERS_CACHE'] = '/home/hf_cache'

# Configuration
DEVICE = "cuda:0"
MAX_NEW_TOKENS = 128
TEMPERATURE = 0.7
NUM_SAMPLES = 20  # More samples for better comparison

def load_model_and_tokenizer(base_model_name, adapter_path=None):
    """Load model with optional LoRA adapter."""
    print(f"Loading {base_model_name}...")
    
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.float16,
        device_map=DEVICE,
        trust_remote_code=True
    )
    
    if adapter_path:
        print(f"Loading adapter from {adapter_path}...")
        model = PeftModel.from_pretrained(model, adapter_path)
        model = model.merge_and_unload()
    
    model.eval()
    return model, tokenizer

def generate_response(model, tokenizer, prompt, max_new_tokens=MAX_NEW_TOKENS):
    """Generate response from model."""
    messages = [
        {"role": "user", "content": prompt}
    ]
    
    input_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(input_text, return_tensors="pt", padding=True).to(DEVICE)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=TEMPERATURE,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    return response.strip()

def prepare_test_set():
    """Prepare test samples from PAWS."""
    print("\n📝 Preparing Paraphrase Test Set (PAWS)...")
    
    dataset = load_dataset("google-research-datasets/paws", "labeled_final", split="test", trust_remote_code=True)
    paraphrases = [item for item in dataset if item['label'] == 1]
    
    random.seed(42)
    selected = random.sample(paraphrases, min(NUM_SAMPLES * 2, len(paraphrases)))
    
    samples = []
    for item in selected[:NUM_SAMPLES]:
        prompt = f"Paraphrase the following sentence:\n\n{item['sentence1']}"
        samples.append({
            "prompt": prompt,
            "input": item['sentence1'],
            "reference": item['sentence2']
        })
    
    print(f"✅ Prepared {len(samples)} paraphrase samples")
    return samples

def evaluate_all_models():
    """Evaluate all 6 paraphrase models + 2 originals."""
    
    print("="*80)
    print("🎯 COMPREHENSIVE PARAPHRASE DATASET COMPARISON")
    print("="*80)
    print()
    print("Testing 8 models:")
    print("  • Original Llama 3.2 3B")
    print("  • Llama 3.2 3B fine-tuned on PAWS-only")
    print("  • Llama 3.2 3B fine-tuned on QQP-only")
    print("  • Llama 3.2 3B fine-tuned on Combined (PAWS+QQP)")
    print("  • Original Llama 3.1 8B")
    print("  • Llama 3.1 8B fine-tuned on PAWS-only")
    print("  • Llama 3.1 8B fine-tuned on QQP-only")
    print("  • Llama 3.1 8B fine-tuned on Combined (PAWS+QQP)")
    print()
    print(f"Samples per model: {NUM_SAMPLES}")
    print(f"Device: {DEVICE}")
    print()
    
    # Prepare test set
    test_samples = prepare_test_set()
    
    # Define models to test
    models_to_test = [
        # 3B models
        {
            "name": "Original 3B",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": None,
            "dataset": "baseline"
        },
        {
            "name": "3B PAWS-only",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": "/home/models/llama32_3b_paws_only_lora",
            "dataset": "paws"
        },
        {
            "name": "3B QQP-only",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": "/home/models/llama32_3b_qqp_only_lora",
            "dataset": "qqp"
        },
        {
            "name": "3B Combined",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": "/home/models/llama32_3b_paraphrase_lora",
            "dataset": "combined"
        },
        # 8B models
        {
            "name": "Original 8B",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": None,
            "dataset": "baseline"
        },
        {
            "name": "8B PAWS-only",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": "/home/models/llama31_8b_paws_only_lora",
            "dataset": "paws"
        },
        {
            "name": "8B QQP-only",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": "/home/models/llama31_8b_qqp_only_lora",
            "dataset": "qqp"
        },
        {
            "name": "8B Combined",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": "/home/models/llama31_8b_paraphrase_lora",
            "dataset": "combined"
        }
    ]
    
    results = []
    
    for model_config in models_to_test:
        print(f"\n🔬 Testing: {model_config['name']}")
        model, tokenizer = load_model_and_tokenizer(model_config['base'], model_config['adapter'])
        
        model_results = []
        for sample in tqdm(test_samples, desc=f"Generating"):
            output = generate_response(model, tokenizer, sample['prompt'])
            model_results.append({
                "input": sample['input'],
                "reference": sample['reference'],
                "output": output
            })
        
        results.append({
            "model": model_config['name'],
            "dataset": model_config['dataset'],
            "results": model_results
        })
        
        # Free memory
        del model
        del tokenizer
        torch.cuda.empty_cache()
    
    # Save results
    output_file = "/home/evaluation_results_paraphrase_dataset_comparison.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Evaluation complete! Results saved to: {output_file}")
    return results

if __name__ == "__main__":
    evaluate_all_models()

