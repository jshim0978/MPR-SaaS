#!/usr/bin/env python3
"""
Evaluate models on HHEM (Hallucination Evaluation) benchmark.
Tests 20 samples to assess factual accuracy and hallucination.
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
MAX_NEW_TOKENS = 256
TEMPERATURE = 0.7
NUM_SAMPLES = 20

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

def load_hhem_samples():
    """Load 20 samples from HHEM/similar hallucination benchmark."""
    print("\n📝 Loading HHEM evaluation samples...")
    
    # Try to load from vectara/hallucination_evaluation_model or similar
    # If not available, use a curated set of factual questions
    
    try:
        # Try loading from HuggingFace
        dataset = load_dataset("vectara/hallucination_evaluation_model", split="train", trust_remote_code=True)
        random.seed(42)
        samples = random.sample(list(dataset), min(NUM_SAMPLES, len(dataset)))
        
        test_samples = []
        for item in samples:
            if 'question' in item and 'answer' in item:
                test_samples.append({
                    "prompt": item['question'],
                    "reference": item.get('answer', ''),
                    "context": item.get('context', '')
                })
        
        print(f"✅ Loaded {len(test_samples)} samples from HHEM benchmark")
        return test_samples
        
    except Exception as e:
        print(f"⚠️  Could not load HHEM benchmark: {e}")
        print("📋 Using curated factual evaluation set instead...")
        
        # Curated set of factual questions for hallucination evaluation
        test_samples = [
            {
                "prompt": "What is the capital of France?",
                "reference": "Paris",
                "context": "Geography question"
            },
            {
                "prompt": "How many planets are in our solar system?",
                "reference": "8 planets (Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune)",
                "context": "Astronomy fact"
            },
            {
                "prompt": "When did World War II end?",
                "reference": "1945",
                "context": "Historical fact"
            },
            {
                "prompt": "Who wrote 'Romeo and Juliet'?",
                "reference": "William Shakespeare",
                "context": "Literature fact"
            },
            {
                "prompt": "What is the speed of light in vacuum?",
                "reference": "299,792,458 meters per second (approximately 300,000 km/s)",
                "context": "Physics constant"
            },
            {
                "prompt": "What is the chemical formula for water?",
                "reference": "H2O",
                "context": "Chemistry fact"
            },
            {
                "prompt": "Who painted the Mona Lisa?",
                "reference": "Leonardo da Vinci",
                "context": "Art history"
            },
            {
                "prompt": "What is the largest ocean on Earth?",
                "reference": "Pacific Ocean",
                "context": "Geography fact"
            },
            {
                "prompt": "How many chromosomes do humans have?",
                "reference": "46 chromosomes (23 pairs)",
                "context": "Biology fact"
            },
            {
                "prompt": "What is the boiling point of water at sea level?",
                "reference": "100 degrees Celsius (212 degrees Fahrenheit)",
                "context": "Physics fact"
            },
            {
                "prompt": "Who developed the theory of relativity?",
                "reference": "Albert Einstein",
                "context": "Science history"
            },
            {
                "prompt": "What is the smallest country in the world?",
                "reference": "Vatican City",
                "context": "Geography fact"
            },
            {
                "prompt": "How many continents are there?",
                "reference": "7 continents",
                "context": "Geography fact"
            },
            {
                "prompt": "What is the chemical symbol for gold?",
                "reference": "Au (from Latin: Aurum)",
                "context": "Chemistry fact"
            },
            {
                "prompt": "Who was the first person to walk on the Moon?",
                "reference": "Neil Armstrong (1969)",
                "context": "Space history"
            },
            {
                "prompt": "What is the largest mammal on Earth?",
                "reference": "Blue whale",
                "context": "Biology fact"
            },
            {
                "prompt": "How many bones are in the adult human body?",
                "reference": "206 bones",
                "context": "Anatomy fact"
            },
            {
                "prompt": "What is the most spoken language in the world?",
                "reference": "English (if counting total speakers including non-native) or Mandarin Chinese (if counting native speakers)",
                "context": "Linguistics fact"
            },
            {
                "prompt": "Who invented the telephone?",
                "reference": "Alexander Graham Bell (1876)",
                "context": "Technology history"
            },
            {
                "prompt": "What is the freezing point of water?",
                "reference": "0 degrees Celsius (32 degrees Fahrenheit)",
                "context": "Physics fact"
            }
        ]
        
        print(f"✅ Created {len(test_samples)} curated factual evaluation samples")
        return test_samples

def evaluate_models():
    """Evaluate all models on HHEM benchmark."""
    print("="*80)
    print("🎯 HHEM EVALUATION - FACTUAL ACCURACY & HALLUCINATION TEST")
    print("="*80)
    
    test_samples = load_hhem_samples()
    
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
        for sample in tqdm(test_samples, desc="Generating responses"):
            output = generate_response(model, tokenizer, sample['prompt'])
            model_results.append({
                "prompt": sample['prompt'],
                "response": output,
                "reference": sample['reference'],
                "context": sample['context']
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
    output_file = "/home/evaluation_hhem_results.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)
    
    print("\n" + "="*80)
    print("✅ EVALUATION COMPLETE!")
    print("="*80)
    print(f"\n📁 Results saved to: {output_file}")
    
    # Print sample outputs
    print("\n" + "="*80)
    print("📊 SAMPLE OUTPUTS (First 3 questions)")
    print("="*80)
    
    for i in range(min(3, len(test_samples))):
        sample = test_samples[i]
        print(f"\n{'─'*80}")
        print(f"📝 Question: {sample['prompt']}")
        print(f"✓ Expected: {sample['reference']}")
        print(f"{'─'*80}")
        
        for result in all_results:
            print(f"\n🔹 {result['model']}:")
            print(result['results'][i]['response'])
            print()
    
    return all_results

def main():
    print("\n🎯 HHEM Evaluation: Factual Accuracy & Hallucination Testing")
    print("   Testing 20 factual questions to assess:")
    print("   • Factual accuracy")
    print("   • Presence of hallucinations")
    print("   • Completeness of answers")
    print()
    
    results = evaluate_models()
    
    print("\n" + "="*80)
    print("📋 NEXT STEPS:")
    print("="*80)
    print("1. Review results: /home/evaluation_hhem_results.json")
    print("2. Check for:")
    print("   • Factual errors or hallucinations")
    print("   • Completeness vs brevity trade-offs")
    print("   • Which model provides most accurate answers")
    print()

if __name__ == "__main__":
    main()

