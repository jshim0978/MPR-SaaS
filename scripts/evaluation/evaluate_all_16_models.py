#!/usr/bin/env python3
"""
Comprehensive evaluation of all 16 fine-tuned models.
Tests each model on its respective task to verify fine-tuning effectiveness.
"""

import os
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from datasets import load_dataset
from tqdm import tqdm
import random
from datetime import datetime

# Set environment
os.environ['HF_HOME'] = '/home/hf_cache'
os.environ['TRANSFORMERS_CACHE'] = '/home/hf_cache'

# Configuration
DEVICE = "cuda:0"
MAX_NEW_TOKENS = 128
TEMPERATURE = 0.7
NUM_SAMPLES = 10  # Quick test with 10 samples per model

def load_model_and_tokenizer(base_model_name, adapter_path=None):
    """Load model with optional LoRA adapter."""
    print(f"  Loading {base_model_name}...")
    
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.float16,
        device_map=DEVICE,
        trust_remote_code=True
    )
    
    if adapter_path:
        print(f"  Loading adapter from {adapter_path}...")
        model = PeftModel.from_pretrained(model, adapter_path)
        model = model.merge_and_unload()
    
    model.eval()
    return model, tokenizer

def generate_response(model, tokenizer, prompt, max_new_tokens=MAX_NEW_TOKENS, system_prompt=None):
    """Generate response from model."""
    if system_prompt:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    else:
        messages = [{"role": "user", "content": prompt}]
    
    input_ids = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(DEVICE)

    with torch.no_grad():
        outputs = model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,
            temperature=TEMPERATURE,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    response = tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True)
    return response

def prepare_grammar_test():
    """Prepare grammar test samples."""
    print("  Preparing grammar test samples...")
    dataset = load_dataset("jfleg", split="test", trust_remote_code=True)
    random.seed(42)
    selected = random.sample(list(dataset), min(NUM_SAMPLES, len(dataset)))
    
    samples = []
    for item in selected[:NUM_SAMPLES]:
        prompt = f"Fix the grammar in this sentence: {item['sentence']}"
        samples.append({
            "prompt": prompt,
            "input": item['sentence'],
            "references": item['corrections']
        })
    
    return samples

def prepare_paraphrase_test():
    """Prepare paraphrase test samples."""
    print("  Preparing paraphrase test samples...")
    dataset = load_dataset("google-research-datasets/paws", "labeled_final", split="test", trust_remote_code=True)
    random.seed(42)
    selected = random.sample(list(dataset), min(NUM_SAMPLES, len(dataset)))
    
    samples = []
    for item in selected[:NUM_SAMPLES]:
        prompt = f"Paraphrase this sentence: {item['sentence1']}"
        samples.append({
            "prompt": prompt,
            "input": item['sentence1'],
            "references": [item['sentence2']]
        })
    
    return samples

def prepare_knowledge_test():
    """Prepare knowledge test samples."""
    print("  Preparing knowledge test samples...")
    dataset = load_dataset("facebook/kilt_tasks", "wow", split="train", trust_remote_code=True)
    random.seed(42)
    selected = random.sample(list(dataset), min(NUM_SAMPLES, len(dataset)))
    
    samples = []
    for item in selected[:NUM_SAMPLES]:
        # KILT WOW structure: item is a dict with 'input' (string) and 'output' (list)
        if isinstance(item['input'], str):
            question = item['input']
        else:
            question = item['input'].get('question', 'Unknown question')
        
        # Handle output format
        if isinstance(item['output'], list) and len(item['output']) > 0:
            if isinstance(item['output'][0], dict):
                references = [o.get('answer', '') for o in item['output'] if o.get('answer')]
            else:
                references = item['output']
        else:
            references = ['No answer available']
        
        # Better prompt for knowledge/description generation
        prompt = question
        
        samples.append({
            "prompt": prompt,
            "input": question,
            "references": references,
            "system_prompt": "You are a knowledgeable assistant. Provide informative, factual descriptions and explanations to answer questions. Focus on delivering comprehensive information rather than just conversational responses."
        })
    
    print(f"  ✅ Prepared {len(samples)} knowledge samples")
    return samples

def evaluate_model_category(category_name, models_config, test_samples):
    """Evaluate all models in a category."""
    print(f"\n{'='*80}")
    print(f"📊 EVALUATING {category_name.upper()}")
    print(f"{'='*80}\n")
    
    results = []
    
    for model_config in models_config:
        print(f"\n🔬 Testing: {model_config['name']}")
        print(f"   Base: {model_config['base']}")
        if model_config['adapter']:
            print(f"   Adapter: {model_config['adapter']}")
        
        model, tokenizer = load_model_and_tokenizer(model_config['base'], model_config['adapter'])
        
        model_results = []
        for sample in tqdm(test_samples, desc=f"  Generating"):
            # Check if sample has a system prompt (for knowledge tasks)
            system_prompt = sample.get('system_prompt', None)
            output = generate_response(model, tokenizer, sample['prompt'], system_prompt=system_prompt)
            model_results.append({
                "input": sample['input'],
                "output": output,
                "references": sample['references']
            })
        
        results.append({
            "model": model_config['name'],
            "base": model_config['base'],
            "adapter": model_config['adapter'],
            "results": model_results
        })
        
        # Free memory
        del model
        del tokenizer
        torch.cuda.empty_cache()
        
        print(f"   ✅ Completed!")
    
    return results

def main():
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║              COMPREHENSIVE MODEL EVALUATION - ALL 16 MODELS              ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print(f"\nTesting {NUM_SAMPLES} samples per model")
    print(f"Device: {DEVICE}\n")

    all_results = {}

    # ========================================================================
    # 1. GRAMMAR MODELS (2 models)
    # ========================================================================
    grammar_models = [
        {
            "name": "Original 3B",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": None
        },
        {
            "name": "3B Grammar (JFLEG)",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": "/home/models/llama32_3b_grammar_lora"
        },
        {
            "name": "Original 8B",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": None
        },
        {
            "name": "8B Grammar (JFLEG)",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": "/home/models/llama31_8b_grammar_lora"
        }
    ]
    grammar_samples = prepare_grammar_test()
    all_results['grammar'] = evaluate_model_category("Grammar (JFLEG)", grammar_models, grammar_samples)

    # ========================================================================
    # 2. PARAPHRASE MODELS (8 models: Original + 3 variants × 2 sizes)
    # ========================================================================
    paraphrase_models_3b = [
        {
            "name": "Original 3B",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": None
        },
        {
            "name": "3B Paraphrase (Combined)",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": "/home/models/llama32_3b_paraphrase_lora"
        },
        {
            "name": "3B Paraphrase (PAWS-only)",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": "/home/models/llama32_3b_paws_only_lora"
        },
        {
            "name": "3B Paraphrase (QQP-only)",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": "/home/models/llama32_3b_qqp_only_lora"
        }
    ]
    
    paraphrase_models_8b = [
        {
            "name": "Original 8B",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": None
        },
        {
            "name": "8B Paraphrase (Combined)",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": "/home/models/llama31_8b_paraphrase_lora"
        },
        {
            "name": "8B Paraphrase (PAWS-only)",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": "/home/models/llama31_8b_paws_only_lora"
        },
        {
            "name": "8B Paraphrase (QQP-only)",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": "/home/models/llama31_8b_qqp_only_lora"
        }
    ]
    
    paraphrase_samples = prepare_paraphrase_test()
    all_results['paraphrase_3b'] = evaluate_model_category("Paraphrase 3B Models", paraphrase_models_3b, paraphrase_samples)
    all_results['paraphrase_8b'] = evaluate_model_category("Paraphrase 8B Models", paraphrase_models_8b, paraphrase_samples)

    # ========================================================================
    # 3. KNOWLEDGE MODELS (10 models: Original + 4 variants × 2 sizes)
    # ========================================================================
    knowledge_models_3b = [
        {
            "name": "Original 3B",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": None
        },
        {
            "name": "3B Knowledge (Combined)",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": "/home/models/llama32_3b_knowledge_lora"
        },
        {
            "name": "3B Knowledge (Wikidata)",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": "/home/models/llama32_3b_wikidata_only_lora"
        },
        {
            "name": "3B Knowledge (Wikipedia)",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": "/home/models/llama32_3b_wikipedia_only_lora"
        },
        {
            "name": "3B Knowledge (KILT WOW)",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": "/home/models/llama32_3b_kilt_wow_only_lora"
        }
    ]
    
    knowledge_models_8b = [
        {
            "name": "Original 8B",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": None
        },
        {
            "name": "8B Knowledge (Combined)",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": "/home/models/llama31_8b_knowledge_lora"
        },
        {
            "name": "8B Knowledge (Wikidata)",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": "/home/models/llama31_8b_wikidata_only_lora"
        },
        {
            "name": "8B Knowledge (Wikipedia)",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": "/home/models/llama31_8b_wikipedia_only_lora"
        },
        {
            "name": "8B Knowledge (KILT WOW)",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": "/home/models/llama31_8b_kilt_wow_only_lora"
        }
    ]
    
    knowledge_samples = prepare_knowledge_test()
    all_results['knowledge_3b'] = evaluate_model_category("Knowledge 3B Models", knowledge_models_3b, knowledge_samples)
    all_results['knowledge_8b'] = evaluate_model_category("Knowledge 8B Models", knowledge_models_8b, knowledge_samples)

    # Save results
    output_file = "/home/evaluation_results_all_16_models.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"✅ ALL EVALUATIONS COMPLETE!")
    print(f"{'='*80}\n")
    print(f"Results saved to: {output_file}")
    print(f"\nTotal models evaluated: 16")
    print(f"Samples per model: {NUM_SAMPLES}")
    print(f"Total generations: {16 * NUM_SAMPLES} = {16 * NUM_SAMPLES}")

if __name__ == "__main__":
    main()

