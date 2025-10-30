#!/usr/bin/env python3
"""
Compare original vs fine-tuned models on JFLEG test set for grammar correction.
Shows side-by-side comparison of outputs.
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import json
import os
from tqdm import tqdm

def setup_environment():
    """Set up environment variables"""
    os.environ["HF_HOME"] = "/home/hf_cache"
    os.environ["TRANSFORMERS_CACHE"] = "/home/hf_cache"
    os.environ["LD_LIBRARY_PATH"] = (
        "/usr/local/lib/python3.12/site-packages/nvidia/nccl/lib:"
        "/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:"
        "/usr/local/lib/python3.12/site-packages/nvidia/cuda_cupti/lib:"
        "/usr/local/cuda-12.9/extras/CUPTI/lib64:" + 
        os.environ.get("LD_LIBRARY_PATH", "")
    )

def load_model(base_model_name, adapter_path=None):
    """Load model (with optional LoRA adapter)"""
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.bfloat16,
    ).to("cuda:0")
    
    if adapter_path:
        model = PeftModel.from_pretrained(base_model, adapter_path)
    else:
        model = base_model
    
    model.eval()
    return model, tokenizer

def generate_correction(model, tokenizer, incorrect_text):
    """Generate grammar correction for a given text"""
    prompt = f"Please correct the grammatical errors in this sentence: {incorrect_text}"
    
    messages = [{"role": "user", "content": prompt}]
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to("cuda:0")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )
    
    generated = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[-1]:],
        skip_special_tokens=True
    ).strip()
    
    return generated

def load_test_data(num_samples=20):
    """Load JFLEG test data"""
    test_file = "/home/data/jfleg_all_corrections_test.jsonl"
    
    samples = []
    with open(test_file, 'r') as f:
        for line in f:
            data = json.loads(line)
            # Extract original (incorrect) and corrected text
            messages = data['messages']
            for i, msg in enumerate(messages):
                if msg['role'] == 'user':
                    original = msg['content']
                elif msg['role'] == 'assistant':
                    corrected = msg['content']
            
            samples.append({
                'original': original,
                'reference': corrected
            })
            
            if len(samples) >= num_samples:
                break
    
    return samples

def compare_models_on_sample(sample_idx, sample, models_dict):
    """Compare all models on a single sample"""
    print(f"\n{'='*80}")
    print(f"Sample {sample_idx + 1}")
    print(f"{'='*80}")
    print(f"📝 Original (Incorrect): {sample['original']}")
    print(f"✅ Reference (Correct):  {sample['reference']}")
    print(f"{'-'*80}")
    
    results = {}
    
    for model_name, (model, tokenizer) in models_dict.items():
        correction = generate_correction(model, tokenizer, sample['original'])
        results[model_name] = correction
        print(f"{model_name:25s}: {correction}")
    
    return results

def main():
    print("🔍 Comparing Original vs Fine-tuned Models on JFLEG Test Set")
    print("="*80)
    
    setup_environment()
    
    # Load test data
    print("\n📂 Loading JFLEG test data...")
    test_samples = load_test_data(num_samples=20)
    print(f"✅ Loaded {len(test_samples)} test samples")
    
    # Load all models
    print("\n📦 Loading models (this may take a while)...")
    models = {}
    
    print("  Loading Llama 3.2 3B Original...")
    models["3B Original"] = load_model("meta-llama/Llama-3.2-3B-Instruct")
    
    print("  Loading Llama 3.2 3B Fine-tuned...")
    models["3B Fine-tuned"] = load_model(
        "meta-llama/Llama-3.2-3B-Instruct",
        "/home/models/llama32_3b_lora_factory"
    )
    
    torch.cuda.empty_cache()
    
    print("  Loading Llama 3.1 8B Original...")
    models["8B Original"] = load_model("meta-llama/Llama-3.1-8B-Instruct")
    
    print("  Loading Llama 3.1 8B Fine-tuned...")
    models["8B Fine-tuned"] = load_model(
        "meta-llama/Llama-3.1-8B-Instruct",
        "/home/models/llama31_8b_lora_factory"
    )
    
    print("✅ All models loaded!")
    
    # Run comparison
    print("\n🧪 Running comparison on test samples...")
    print("(This will take a few minutes)")
    
    all_results = []
    
    for idx, sample in enumerate(test_samples):
        results = compare_models_on_sample(idx, sample, models)
        all_results.append({
            'sample': sample,
            'results': results
        })
    
    # Summary statistics
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"Total samples evaluated: {len(test_samples)}")
    print("\nModel outputs saved above for manual inspection.")
    print("\n✅ Comparison complete!")
    print("\n💡 Look for patterns:")
    print("   - Are fine-tuned models more concise?")
    print("   - Do they correct errors more accurately?")
    print("   - Are they closer to the reference corrections?")
    
    # Save results to file
    output_file = "/home/comparison_results.txt"
    with open(output_file, 'w') as f:
        f.write("JFLEG Test Set Comparison: Original vs Fine-tuned Models\n")
        f.write("="*80 + "\n\n")
        
        for idx, result in enumerate(all_results):
            sample = result['sample']
            outputs = result['results']
            
            f.write(f"Sample {idx + 1}\n")
            f.write(f"{'='*80}\n")
            f.write(f"Original (Incorrect): {sample['original']}\n")
            f.write(f"Reference (Correct):  {sample['reference']}\n")
            f.write(f"{'-'*80}\n")
            
            for model_name, output in outputs.items():
                f.write(f"{model_name:25s}: {output}\n")
            
            f.write("\n\n")
    
    print(f"\n📁 Detailed results saved to: {output_file}")

if __name__ == "__main__":
    main()

