#!/usr/bin/env python3
"""
Test both fine-tuned models to ensure they can generate text properly.
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import os
import sys

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

def load_finetuned_model(base_model_name, adapter_path, model_display_name):
    """Load a fine-tuned model with LoRA adapter"""
    print(f"\n{'='*60}")
    print(f"Testing: {model_display_name}")
    print(f"{'='*60}")
    print(f"📦 Loading base model: {base_model_name}")
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load base model on GPU with bfloat16
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.bfloat16,
    ).to("cuda:0")
    
    print(f"🔧 Loading LoRA adapter from: {adapter_path}")
    
    # Load LoRA adapter
    model = PeftModel.from_pretrained(base_model, adapter_path)
    model.eval()
    
    print(f"✅ Model loaded successfully on cuda:0")
    
    return model, tokenizer

def test_model(model, tokenizer, model_name):
    """Test model with various prompts"""
    
    test_cases = [
        {
            "name": "Grammar Correction (Training Task)",
            "prompt": "Please correct the grammatical errors in this sentence: I am go to the store yesterday."
        },
        {
            "name": "Simple Question",
            "prompt": "Who are you?"
        },
        {
            "name": "Grammar Correction 2",
            "prompt": "Fix the grammar: She don't likes reading books."
        },
        {
            "name": "Grammar Correction 3",
            "prompt": "Correct this: They was playing in the park when it start raining."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'─'*60}")
        print(f"Test {i}: {test_case['name']}")
        print(f"{'─'*60}")
        print(f"Input: {test_case['prompt']}")
        
        # Prepare messages
        messages = [{"role": "user", "content": test_case['prompt']}]
        
        # Tokenize
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to("cuda:0")
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                do_sample=False,  # Greedy decoding for consistent results
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode
        generated_text = tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[-1]:],
            skip_special_tokens=True
        )
        
        print(f"Output: {generated_text}")
        
        # Basic sanity checks
        if not generated_text or generated_text.strip() == "":
            print("❌ WARNING: Empty output!")
            return False
        
        if generated_text == "!" * len(generated_text):
            print("❌ WARNING: Only exclamation marks!")
            return False
        
        if len(generated_text) < 5:
            print("⚠️  WARNING: Very short output (might be normal for some prompts)")
    
    print(f"\n{'='*60}")
    print(f"✅ {model_name} PASSED all generation tests!")
    print(f"{'='*60}")
    return True

def main():
    print("🔧 Testing Fine-tuned Models")
    print("="*60)
    
    setup_environment()
    
    all_passed = True
    
    # Test Llama 3.2 3B
    try:
        model_3b, tokenizer_3b = load_finetuned_model(
            "meta-llama/Llama-3.2-3B-Instruct",
            "/home/models/llama32_3b_lora_factory",
            "Llama 3.2 3B Fine-tuned"
        )
        
        passed_3b = test_model(model_3b, tokenizer_3b, "Llama 3.2 3B")
        all_passed = all_passed and passed_3b
        
        # Clean up
        del model_3b, tokenizer_3b
        torch.cuda.empty_cache()
        
    except Exception as e:
        print(f"❌ ERROR testing Llama 3.2 3B: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    # Test Llama 3.1 8B
    try:
        model_8b, tokenizer_8b = load_finetuned_model(
            "meta-llama/Llama-3.1-8B-Instruct",
            "/home/models/llama31_8b_lora_factory",
            "Llama 3.1 8B Fine-tuned"
        )
        
        passed_8b = test_model(model_8b, tokenizer_8b, "Llama 3.1 8B")
        all_passed = all_passed and passed_8b
        
        # Clean up
        del model_8b, tokenizer_8b
        torch.cuda.empty_cache()
        
    except Exception as e:
        print(f"❌ ERROR testing Llama 3.1 8B: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    # Final summary
    print("\n" + "="*60)
    print("📊 FINAL SUMMARY")
    print("="*60)
    
    if all_passed:
        print("✅ All fine-tuned models working correctly!")
        print("✅ Ready for comparison with original models!")
        return 0
    else:
        print("❌ Some models failed generation tests")
        print("⚠️  Please review errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())

