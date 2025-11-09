#!/usr/bin/env python3
"""
OPRO (Optimization by PROmpting) Baseline
==========================================

Paper: Yang et al., 2023 - "Large Language Models as Optimizers"
Repo: https://github.com/google-deepmind/opro

Synchronized with jw1's configuration:
- Model: Llama-3.2-3B-Instruct
- Temperature: 0.2, Top-p: 0.9, Seed: 13
"""

import time
import torch
from typing import Dict, Any

def opro_refine(prompt: str, model, tokenizer, device=None) -> Dict[str, Any]:
    """
    OPRO: Uses LLM as meta-optimizer to improve prompts.
    
    Algorithm:
    1. Generate meta-prompt asking for improvements
    2. Use Llama-3.2-3B to generate improved version
    3. Clean and validate output
    
    Budget: 1 iteration (simplified from 8 for fair comparison)
    """
    start_time = time.time()
    
    # Use provided device or model's device
    if device is None:
        device = model.device
    
    # Meta-prompt for optimization
    meta_prompt = f"""You are a prompt optimizer. Improve the following prompt to be more specific, clear, and effective.

Original prompt: {prompt}

Generate an improved version that:
1. Is more specific and clear
2. Preserves the original intent
3. Reduces ambiguity
4. Maintains conciseness

Improved prompt:"""
    
    # Tokenize
    inputs = tokenizer(meta_prompt, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    input_tokens = inputs['input_ids'].shape[1]
    
    # Generate with fixed seed
    torch.manual_seed(13)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.2,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    output_tokens = outputs.shape[1] - input_tokens
    
    # Decode
    raw_output = tokenizer.decode(outputs[0][input_tokens:], skip_special_tokens=True).strip()
    
    # Parse refined prompt (it's usually in the first line or after a marker)
    if "Improved prompt:" in raw_output:
        refined_prompt = raw_output.split("Improved prompt:")[-1].strip()
    else:
        # Take the first non-empty line as the refined prompt
        lines = [line.strip() for line in raw_output.split('\n') if line.strip()]
        refined_prompt = lines[0] if lines else prompt
    
    # Remove any trailing explanations (stop at "Changes made:", "This", etc.)
    for stop_marker in ['\n\nChanges', '\n\nThis', '\n\nNote:', '\nChanges', '\nThis']:
        if stop_marker in refined_prompt:
            refined_prompt = refined_prompt.split(stop_marker)[0].strip()
    
    # Fallback to original if refinement is too short
    if len(refined_prompt) < 10:
        refined_prompt = prompt
    
    latency_ms = (time.time() - start_time) * 1000
    
    return {
        "method": "OPRO",
        "original": prompt,
        "refined": refined_prompt,
        "latency_ms": latency_ms,
        "tokens_input": input_tokens,
        "tokens_output": output_tokens,
        "tokens_total": input_tokens + output_tokens
    }

