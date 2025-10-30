#!/usr/bin/env python3
"""
Evaluate Wikipedia-only, Wikidata-only, and Wikipedia+Wikidata models.
Excludes KILT WOW-trained models.
Tests on 20 HHEM factual questions.
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

def get_test_questions():
    """Get 20 factual test questions."""
    return [
        {
            "prompt": "What is the capital of France?",
            "reference": "Paris",
            "context": "Geography"
        },
        {
            "prompt": "How many planets are in our solar system?",
            "reference": "8 planets",
            "context": "Astronomy"
        },
        {
            "prompt": "When did World War II end?",
            "reference": "1945",
            "context": "History"
        },
        {
            "prompt": "Who wrote 'Romeo and Juliet'?",
            "reference": "William Shakespeare",
            "context": "Literature"
        },
        {
            "prompt": "What is the speed of light in vacuum?",
            "reference": "299,792,458 meters per second",
            "context": "Physics"
        },
        {
            "prompt": "What is the chemical formula for water?",
            "reference": "H2O",
            "context": "Chemistry"
        },
        {
            "prompt": "Who painted the Mona Lisa?",
            "reference": "Leonardo da Vinci",
            "context": "Art"
        },
        {
            "prompt": "What is the largest ocean on Earth?",
            "reference": "Pacific Ocean",
            "context": "Geography"
        },
        {
            "prompt": "How many chromosomes do humans have?",
            "reference": "46 chromosomes (23 pairs)",
            "context": "Biology"
        },
        {
            "prompt": "What is the boiling point of water at sea level?",
            "reference": "100 degrees Celsius",
            "context": "Physics"
        },
        {
            "prompt": "Who developed the theory of relativity?",
            "reference": "Albert Einstein",
            "context": "Science"
        },
        {
            "prompt": "What is the smallest country in the world?",
            "reference": "Vatican City",
            "context": "Geography"
        },
        {
            "prompt": "How many continents are there?",
            "reference": "7 continents",
            "context": "Geography"
        },
        {
            "prompt": "What is the chemical symbol for gold?",
            "reference": "Au",
            "context": "Chemistry"
        },
        {
            "prompt": "Who was the first person to walk on the Moon?",
            "reference": "Neil Armstrong",
            "context": "History"
        },
        {
            "prompt": "What is the largest mammal on Earth?",
            "reference": "Blue whale",
            "context": "Biology"
        },
        {
            "prompt": "How many bones are in the adult human body?",
            "reference": "206 bones",
            "context": "Anatomy"
        },
        {
            "prompt": "What is the most spoken language in the world?",
            "reference": "English or Mandarin Chinese",
            "context": "Linguistics"
        },
        {
            "prompt": "Who invented the telephone?",
            "reference": "Alexander Graham Bell",
            "context": "Technology"
        },
        {
            "prompt": "What is the freezing point of water?",
            "reference": "0 degrees Celsius",
            "context": "Physics"
        }
    ]

def evaluate_models():
    """Evaluate Wikipedia-focused models only (no KILT WOW)."""
    print("="*80)
    print("🧠 WIKIPEDIA-FOCUSED MODELS EVALUATION")
    print("="*80)
    print("\nExcluding: KILT WOW (conversational dialogue)")
    print("Testing: Wikipedia-only, Wikidata-only, Wiki+Wikidata\n")
    
    test_questions = get_test_questions()
    print(f"📝 Testing on {len(test_questions)} factual questions\n")
    
    models_to_test = [
        {
            "name": "3B Wikipedia-only",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": "/home/models/llama32_3b_wikipedia_only_lora"
        },
        {
            "name": "3B Wikidata-only",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": "/home/models/llama32_3b_wikidata_only_lora"
        },
        {
            "name": "3B Wiki+Wikidata (no KILT)",
            "base": "meta-llama/Llama-3.2-3B-Instruct",
            "adapter": "/home/models/llama32_3b_knowledge_wiki_only_lora"
        },
        {
            "name": "8B Wikipedia-only",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": "/home/models/llama31_8b_wikipedia_only_lora"
        },
        {
            "name": "8B Wikidata-only",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": "/home/models/llama31_8b_wikidata_only_lora"
        },
        {
            "name": "8B Wiki+Wikidata (no KILT)",
            "base": "meta-llama/Llama-3.1-8B-Instruct",
            "adapter": "/home/models/llama31_8b_knowledge_wiki_only_lora"
        }
    ]
    
    all_results = []
    
    for model_config in models_to_test:
        print(f"\n{'='*80}")
        print(f"🔬 Testing: {model_config['name']}")
        print(f"{'='*80}")
        
        model, tokenizer = load_model_and_tokenizer(model_config['base'], model_config['adapter'])
        
        model_results = []
        for question in tqdm(test_questions, desc="Generating responses"):
            output = generate_response(model, tokenizer, question['prompt'])
            model_results.append({
                "prompt": question['prompt'],
                "response": output,
                "reference": question['reference'],
                "context": question['context']
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
    output_file = "/home/evaluation_wiki_models_only.json"
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
    
    for i in range(min(3, len(test_questions))):
        question = test_questions[i]
        print(f"\n{'─'*80}")
        print(f"📝 Question: {question['prompt']}")
        print(f"✓ Expected: {question['reference']}")
        print(f"{'─'*80}")
        
        for result in all_results:
            response = result['results'][i]['response']
            word_count = len(response.split())
            print(f"\n🔹 {result['model']} ({word_count} words):")
            if len(response) > 150:
                print(f"{response[:150]}...")
            else:
                print(response)
    
    return all_results

def main():
    print("\n🎯 Wikipedia-Focused Models Evaluation")
    print("   Testing models trained WITHOUT KILT WOW dialogues")
    print("   Focus: Wikipedia-only, Wikidata-only, Wiki+Wikidata combined\n")
    
    results = evaluate_models()
    
    print("\n" + "="*80)
    print("📋 NEXT STEPS:")
    print("="*80)
    print("1. Review results: /home/evaluation_wiki_models_only.json")
    print("2. Run analysis script to compare response styles")
    print("3. Determine which training approach produces desired output\n")

if __name__ == "__main__":
    main()

