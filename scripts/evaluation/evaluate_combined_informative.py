#!/usr/bin/env python3
"""
Evaluation script specifically for the Wikipedia + Wikidata combined models.
Tests whether they produce informative, factual descriptions.
"""

import os
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from tqdm import tqdm

# Set environment
os.environ['HF_HOME'] = '/home/hf_cache'
os.environ['TRANSFORMERS_CACHE'] = '/home/hf_cache'

# Configuration
DEVICE = "cuda:0"
MAX_NEW_TOKENS = 256
TEMPERATURE = 0.7

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

def generate_response(model, tokenizer, prompt, max_new_tokens=MAX_NEW_TOKENS, system_prompt=None):
    """Generate response from model."""
    if system_prompt:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    else:
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

def get_test_prompts():
    """Test prompts that should elicit informative, factual descriptions."""
    return [
        # General knowledge questions
        "What is photosynthesis?",
        "Explain what the Eiffel Tower is.",
        "What is machine learning?",
        "Tell me about the Great Wall of China.",
        "What is cryptocurrency?",
        
        # Entity-focused questions
        "Who was Albert Einstein?",
        "Who is Marie Curie?",
        "Who was Leonardo da Vinci?",
        "What is NASA?",
        "What is the United Nations?",
        
        # Process/how-to questions
        "How does a car engine work?",
        "How do vaccines work?",
        "How is chocolate made?",
        "How does WiFi work?",
        "How do airplanes fly?",
        
        # Statistical/factual questions (testing for specific data)
        "How often should adults get haircuts?",
        "What is the average human lifespan?",
        "How tall is Mount Everest?",
        "What is the speed of light?",
        "How many bones are in the human body?",
        
        # Comparison questions
        "What is the difference between bacteria and viruses?",
        "What is the difference between weather and climate?",
        "How are stars and planets different?",
        "What's the difference between HTTP and HTTPS?",
        "What distinguishes mammals from reptiles?"
    ]

def evaluate_models():
    """Evaluate both 3B and 8B combined models."""
    print("="*80)
    print("🧠 EVALUATING COMBINED (WIKIPEDIA + WIKIDATA) MODELS")
    print("="*80)
    
    test_prompts = get_test_prompts()
    print(f"\n📝 Testing {len(test_prompts)} prompts designed to elicit informative responses")
    
    models_to_test = [
        {
            "name": "Original 3B",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": None
        },
        {
            "name": "3B Combined (Wiki + Wikidata)",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": "/home/models/llama32_3b_knowledge_lora"
        },
        {
            "name": "Original 8B",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": None
        },
        {
            "name": "8B Combined (Wiki + Wikidata)",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": "/home/models/llama31_8b_knowledge_lora"
        }
    ]
    
    all_results = []
    
    for model_config in models_to_test:
        print(f"\n{'='*80}")
        print(f"🔬 Testing: {model_config['name']}")
        print(f"{'='*80}")
        
        model, tokenizer = load_model_and_tokenizer(model_config['base'], model_config['adapter'])
        
        model_results = []
        for prompt in tqdm(test_prompts, desc="Generating responses"):
            output = generate_response(model, tokenizer, prompt)
            model_results.append({
                "prompt": prompt,
                "response": output
            })
        
        all_results.append({
            "model": model_config['name'],
            "results": model_results
        })
        
        # Free memory
        del model
        del tokenizer
        torch.cuda.empty_cache()
    
    # Save results
    output_file = "/home/evaluation_combined_informative.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)
    
    print("\n" + "="*80)
    print("✅ EVALUATION COMPLETE!")
    print("="*80)
    print(f"\n📁 Results saved to: {output_file}")
    
    # Print a few sample outputs for quick review
    print("\n" + "="*80)
    print("📊 SAMPLE OUTPUTS (First 3 prompts)")
    print("="*80)
    
    for i, prompt in enumerate(test_prompts[:3]):
        print(f"\n{'─'*80}")
        print(f"📝 Prompt: {prompt}")
        print(f"{'─'*80}")
        
        for result in all_results:
            print(f"\n🔹 {result['model']}:")
            print(result['results'][i]['response'])
            print()
    
    return all_results

def main():
    print("\n🎯 Evaluating Combined Models for Informative Responses")
    print("   Focus: Testing if models produce factual, detailed, informative descriptions")
    print()
    
    results = evaluate_models()
    
    print("\n" + "="*80)
    print("📋 NEXT STEPS:")
    print("="*80)
    print("1. Review the full results in: /home/evaluation_combined_informative.json")
    print("2. Look for:")
    print("   • Factual, encyclopedia-style responses")
    print("   • Specific data (numbers, statistics, dates)")
    print("   • Detailed explanations vs conversational responses")
    print("   • Whether responses provide informative depth")
    print("\n3. Based on the results, decide:")
    print("   • If combined models show improvement → optimize system prompts")
    print("   • If still too conversational → consider different training data")
    print()

if __name__ == "__main__":
    main()

