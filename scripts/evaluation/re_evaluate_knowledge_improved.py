#!/usr/bin/env python3
"""
Re-evaluate knowledge models with IMPROVED system prompts for informative descriptions.
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
NUM_SAMPLES = 20  # Increased to 20 for better comparison

# IMPROVED SYSTEM PROMPT - Much more directive
SYSTEM_PROMPT = """You are an informative knowledge assistant. When answering questions, provide relevant factual information, statistics, context, and background details that help the user understand the topic better. Focus on:

1. Relevant facts and statistics
2. Common patterns and behaviors related to the topic
3. Historical context or background information
4. Practical information that adds value

Do NOT simply respond conversationally. Always provide informative, educational content."""

def load_model_and_tokenizer(base_model_name, adapter_path=None):
    """Load model with optional LoRA adapter."""
    
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

def prepare_knowledge_test():
    """Prepare knowledge test samples with IMPROVED system prompt."""
    print("  Preparing knowledge test samples...")
    dataset = load_dataset("facebook/kilt_tasks", "wow", split="train", trust_remote_code=True)
    random.seed(42)
    selected = random.sample(list(dataset), min(NUM_SAMPLES, len(dataset)))
    
    samples = []
    for item in selected[:NUM_SAMPLES]:
        # KILT WOW structure
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
        
        samples.append({
            "prompt": question,
            "input": question,
            "references": references,
            "system_prompt": SYSTEM_PROMPT
        })
    
    print(f"  ✅ Prepared {len(samples)} knowledge samples")
    return samples

def evaluate_knowledge_models():
    """Evaluate all knowledge models."""
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║      RE-EVALUATING KNOWLEDGE MODELS WITH IMPROVED SYSTEM PROMPTS         ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print("")
    print("System Prompt:")
    print(SYSTEM_PROMPT)
    print("")
    
    # Prepare test samples
    knowledge_samples = prepare_knowledge_test()
    
    # Knowledge models configuration
    knowledge_models_3b = [
        {"name": "Original 3B", "base": "meta-llama/Llama-3.2-3B-Instruct", "adapter": None},
        {"name": "3B Knowledge (Combined)", "base": "meta-llama/Llama-3.2-3B-Instruct", "adapter": "/home/models/llama32_3b_knowledge_lora"},
        {"name": "3B Knowledge (Wikidata)", "base": "meta-llama/Llama-3.2-3B-Instruct", "adapter": "/home/models/llama32_3b_wikidata_only_lora"},
        {"name": "3B Knowledge (Wikipedia)", "base": "meta-llama/Llama-3.2-3B-Instruct", "adapter": "/home/models/llama32_3b_wikipedia_only_lora"},
        {"name": "3B Knowledge (KILT WOW)", "base": "meta-llama/Llama-3.2-3B-Instruct", "adapter": "/home/models/llama32_3b_kilt_wow_only_lora"}
    ]
    
    knowledge_models_8b = [
        {"name": "Original 8B", "base": "meta-llama/Llama-3.1-8B-Instruct", "adapter": None},
        {"name": "8B Knowledge (Combined)", "base": "meta-llama/Llama-3.1-8B-Instruct", "adapter": "/home/models/llama31_8b_knowledge_lora"},
        {"name": "8B Knowledge (Wikidata)", "base": "meta-llama/Llama-3.1-8B-Instruct", "adapter": "/home/models/llama31_8b_wikidata_only_lora"},
        {"name": "8B Knowledge (Wikipedia)", "base": "meta-llama/Llama-3.1-8B-Instruct", "adapter": "/home/models/llama31_8b_wikipedia_only_lora"},
        {"name": "8B Knowledge (KILT WOW)", "base": "meta-llama/Llama-3.1-8B-Instruct", "adapter": "/home/models/llama31_8b_kilt_wow_only_lora"}
    ]
    
    all_knowledge_models = knowledge_models_3b + knowledge_models_8b
    
    results_3b = []
    results_8b = []
    
    print("\n" + "="*80)
    print("📊 EVALUATING KNOWLEDGE MODELS (3B)")
    print("="*80 + "\n")
    
    for model_config in knowledge_models_3b:
        print(f"\n🔬 Testing: {model_config['name']}")
        print(f"   Base: {model_config['base']}")
        if model_config['adapter']:
            print(f"   Adapter: {model_config['adapter']}")
        
        model, tokenizer = load_model_and_tokenizer(model_config['base'], model_config['adapter'])
        
        model_results = []
        for sample in tqdm(knowledge_samples, desc=f"  Generating"):
            output = generate_response(
                model, 
                tokenizer, 
                sample['prompt'], 
                system_prompt=sample['system_prompt']
            )
            model_results.append({
                "input": sample['input'],
                "output": output,
                "references": sample['references']
            })
        
        results_3b.append({
            "model": model_config['name'],
            "base": model_config['base'],
            "adapter": model_config['adapter'],
            "results": model_results
        })
        print("   ✅ Completed!")
        
        # Free memory
        del model
        del tokenizer
        torch.cuda.empty_cache()
    
    print("\n" + "="*80)
    print("📊 EVALUATING KNOWLEDGE MODELS (8B)")
    print("="*80 + "\n")
    
    for model_config in knowledge_models_8b:
        print(f"\n🔬 Testing: {model_config['name']}")
        print(f"   Base: {model_config['base']}")
        if model_config['adapter']:
            print(f"   Adapter: {model_config['adapter']}")
        
        model, tokenizer = load_model_and_tokenizer(model_config['base'], model_config['adapter'])
        
        model_results = []
        for sample in tqdm(knowledge_samples, desc=f"  Generating"):
            output = generate_response(
                model, 
                tokenizer, 
                sample['prompt'], 
                system_prompt=sample['system_prompt']
            )
            model_results.append({
                "input": sample['input'],
                "output": output,
                "references": sample['references']
            })
        
        results_8b.append({
            "model": model_config['name'],
            "base": model_config['base'],
            "adapter": model_config['adapter'],
            "results": model_results
        })
        print("   ✅ Completed!")
        
        # Free memory
        del model
        del tokenizer
        torch.cuda.empty_cache()
    
    # Save results
    all_results = {
        "knowledge_3b": results_3b,
        "knowledge_8b": results_8b,
        "system_prompt_used": SYSTEM_PROMPT
    }
    
    output_file = "/home/evaluation_results_knowledge_improved_prompt.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*80}")
    print("✅ KNOWLEDGE EVALUATION COMPLETE!")
    print(f"{'='*80}\n")
    print(f"Results saved to: {output_file}")
    print(f"\nTotal models evaluated: {len(all_knowledge_models)}")
    print(f"Samples per model: {NUM_SAMPLES}")
    print(f"Total generations: {len(all_knowledge_models) * NUM_SAMPLES}")
    print(f"\nCompleted at: {datetime.now().strftime('%Y. %m. %d. (%a) %H:%M:%S KST')}\n")

if __name__ == "__main__":
    evaluate_knowledge_models()

