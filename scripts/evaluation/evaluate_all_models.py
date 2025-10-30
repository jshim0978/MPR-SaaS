#!/usr/bin/env python3
"""
Comprehensive evaluation script for all fine-tuned models.
Tests grammar correction, paraphrasing, and knowledge tasks.
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
NUM_SAMPLES = 100

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
    
    input_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    inputs = tokenizer(input_text, return_tensors="pt").to(DEVICE)
    
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

def prepare_grammar_test_set():
    """Prepare 100 grammar correction test samples from JFLEG."""
    print("\n📝 Preparing Grammar Test Set (JFLEG)...")
    dataset = load_dataset("jfleg", split="test", trust_remote_code=True)
    
    samples = []
    for i, item in enumerate(dataset):
        if i >= NUM_SAMPLES:
            break
        samples.append({
            "input": item['sentence'],
            "references": item['corrections'],
            "prompt": f"Correct the grammar in this sentence: {item['sentence']}"
        })
    
    print(f"✅ Prepared {len(samples)} grammar samples")
    return samples

def prepare_paraphrase_test_set():
    """Prepare 100 paraphrasing test samples."""
    print("\n🔄 Preparing Paraphrase Test Set (PAWS)...")
    dataset = load_dataset("google-research-datasets/paws", "labeled_final", split="test", trust_remote_code=True)
    
    # Filter for positive paraphrases
    positive_pairs = [item for item in dataset if item['label'] == 1]
    random.seed(42)
    selected = random.sample(positive_pairs, min(NUM_SAMPLES, len(positive_pairs)))
    
    samples = []
    for item in selected:
        samples.append({
            "input": item['sentence1'],
            "reference": item['sentence2'],
            "prompt": f"Paraphrase this sentence: {item['sentence1']}"
        })
    
    print(f"✅ Prepared {len(samples)} paraphrase samples")
    return samples

def prepare_knowledge_test_set():
    """Prepare 100 knowledge test samples."""
    print("\n🧠 Preparing Knowledge Test Set...")
    
    # Load KILT wizard_of_wikipedia (config name is 'wow')
    dataset = load_dataset("facebook/kilt_tasks", "wow", split="train", trust_remote_code=True)
    
    random.seed(42)
    selected = random.sample(list(dataset), min(NUM_SAMPLES, len(dataset)))
    
    samples = []
    for item in selected[:NUM_SAMPLES]:
        if 'input' in item and item['input']:
            samples.append({
                "input": item['input'],
                "prompt": item['input']
            })
    
    print(f"✅ Prepared {len(samples)} knowledge samples")
    return samples[:NUM_SAMPLES]

def evaluate_grammar_models():
    """Evaluate grammar (JFLEG) fine-tuned models."""
    print("\n" + "="*80)
    print("📝 EVALUATING GRAMMAR MODELS")
    print("="*80)
    
    test_samples = prepare_grammar_test_set()
    
    models_to_test = [
        {
            "name": "Original 3B",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": None
        },
        {
            "name": "Fine-tuned 3B (JFLEG)",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": "/home/models/llama32_3b_grammar_lora"
        },
        {
            "name": "Original 8B",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": None
        },
        {
            "name": "Fine-tuned 8B (JFLEG)",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": "/home/models/llama31_8b_grammar_lora"
        }
    ]
    
    results = []
    
    # Test first 10 samples for quick comparison
    test_subset = test_samples[:10]
    
    for model_config in models_to_test:
        print(f"\n🔬 Testing: {model_config['name']}")
        model, tokenizer = load_model_and_tokenizer(model_config['base'], model_config['adapter'])
        
        model_results = []
        for sample in tqdm(test_subset, desc=f"Generating"):
            output = generate_response(model, tokenizer, sample['prompt'])
            model_results.append({
                "input": sample['input'],
                "output": output,
                "references": sample['references']
            })
        
        results.append({
            "model": model_config['name'],
            "results": model_results
        })
        
        # Free memory
        del model
        del tokenizer
        torch.cuda.empty_cache()
    
    # Save results
    with open("/home/evaluation_results_grammar.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n✅ Grammar evaluation complete!")
    return results

def evaluate_paraphrase_models():
    """Evaluate paraphrasing fine-tuned models."""
    print("\n" + "="*80)
    print("🔄 EVALUATING PARAPHRASE MODELS")
    print("="*80)
    
    test_samples = prepare_paraphrase_test_set()
    
    models_to_test = [
        {
            "name": "Original 3B",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": None
        },
        {
            "name": "Fine-tuned 3B (Paraphrase)",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": "/home/models/llama32_3b_paraphrase_lora"
        },
        {
            "name": "Original 8B",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": None
        },
        {
            "name": "Fine-tuned 8B (Paraphrase)",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": "/home/models/llama31_8b_paraphrase_lora"
        }
    ]
    
    results = []
    
    # Test first 10 samples for quick comparison
    test_subset = test_samples[:10]
    
    for model_config in models_to_test:
        print(f"\n🔬 Testing: {model_config['name']}")
        model, tokenizer = load_model_and_tokenizer(model_config['base'], model_config['adapter'])
        
        model_results = []
        for sample in tqdm(test_subset, desc=f"Generating"):
            output = generate_response(model, tokenizer, sample['prompt'])
            model_results.append({
                "input": sample['input'],
                "output": output,
                "reference": sample['reference']
            })
        
        results.append({
            "model": model_config['name'],
            "results": model_results
        })
        
        # Free memory
        del model
        del tokenizer
        torch.cuda.empty_cache()
    
    # Save results
    with open("/home/evaluation_results_paraphrase.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n✅ Paraphrase evaluation complete!")
    return results

def evaluate_knowledge_models():
    """Evaluate knowledge fine-tuned models."""
    print("\n" + "="*80)
    print("🧠 EVALUATING KNOWLEDGE MODELS")
    print("="*80)
    
    test_samples = prepare_knowledge_test_set()
    
    models_to_test = [
        {
            "name": "Original 3B",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": None
        },
        {
            "name": "Fine-tuned 3B (Knowledge)",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": "/home/models/llama32_3b_knowledge_lora"
        },
        {
            "name": "Original 8B",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": None
        },
        {
            "name": "Fine-tuned 8B (Knowledge)",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": "/home/models/llama31_8b_knowledge_lora"
        }
    ]
    
    results = []
    
    # Test first 10 samples for quick comparison
    test_subset = test_samples[:10]
    
    for model_config in models_to_test:
        print(f"\n🔬 Testing: {model_config['name']}")
        model, tokenizer = load_model_and_tokenizer(model_config['base'], model_config['adapter'])
        
        model_results = []
        for sample in tqdm(test_subset, desc=f"Generating"):
            output = generate_response(model, tokenizer, sample['prompt'])
            model_results.append({
                "input": sample['input'],
                "output": output
            })
        
        results.append({
            "model": model_config['name'],
            "results": model_results
        })
        
        # Free memory
        del model
        del tokenizer
        torch.cuda.empty_cache()
    
    # Save results
    with open("/home/evaluation_results_knowledge.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n✅ Knowledge evaluation complete!")
    return results

def main():
    print("="*80)
    print("🎯 COMPREHENSIVE MODEL EVALUATION")
    print("="*80)
    print(f"\nTesting 6 models across 3 tasks")
    print(f"Samples per task: 10 (quick comparison)")
    print(f"Device: {DEVICE}")
    print("\n")
    
    # Run all evaluations
    grammar_results = evaluate_grammar_models()
    paraphrase_results = evaluate_paraphrase_models()
    knowledge_results = evaluate_knowledge_models()
    
    print("\n" + "="*80)
    print("✅ ALL EVALUATIONS COMPLETE!")
    print("="*80)
    print("\n📁 Results saved to:")
    print("   • /home/evaluation_results_grammar.json")
    print("   • /home/evaluation_results_paraphrase.json")
    print("   • /home/evaluation_results_knowledge.json")
    print("\n🔍 Run the comparison script to view results:")
    print("   python3 /home/compare_evaluation_results.py")
    print()

if __name__ == "__main__":
    main()

