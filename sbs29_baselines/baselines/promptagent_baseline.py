#!/usr/bin/env python3
"""
PromptAgent Baseline
====================

Paper: Wang et al., 2023 - "PromptAgent: Strategic Planning with Language Models"
Repo: https://github.com/microsoft/promptagent

Synchronized with jw1's configuration:
- Model: Llama-3.2-3B-Instruct
- Temperature: 0.2, Top-p: 0.9, Seed: 13
"""

import time
import torch
from typing import Dict, Any

def promptagent_refine(prompt: str, model, tokenizer, device=None) -> Dict[str, Any]:
    """
    PromptAgent: Strategic planning approach using multi-step analysis.
    
    Algorithm:
    1. Identify core intent
    2. Clarify ambiguities
    3. Add relevant context
    4. Structure for clarity
    
    Budget: Single-pass strategic refinement
    """
    start_time = time.time()
    
    # Use provided device or model's device
    if device is None:
        device = model.device
    
    # Strategic planning prompt
    strategic_prompt = f"""You are a strategic prompt planner. Analyze and improve this prompt:

Original: {prompt}

Improve it by:
1. Identifying the core intent
2. Clarifying any ambiguities
3. Adding helpful context
4. Structuring it clearly

Improved prompt:"""
    
    # Tokenize
    inputs = tokenizer(strategic_prompt, return_tensors="pt", truncation=True, max_length=512)
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
    
    # Parse refined prompt
    if "Improved prompt:" in raw_output:
        refined_prompt = raw_output.split("Improved prompt:")[-1].strip()
    else:
        # Take the first non-empty line
        lines = [line.strip() for line in raw_output.split('\n') if line.strip()]
        refined_prompt = lines[0] if lines else prompt
    
    # Remove trailing explanations
    for stop_marker in ['\n\nChanges', '\n\nThis', '\n\nAnalysis', '\n\nNote:', '\nChanges', '\nThis', '\n\n##']:
        if stop_marker in refined_prompt:
            refined_prompt = refined_prompt.split(stop_marker)[0].strip()
    
    # Fallback if too short
    if len(refined_prompt) < 10:
        refined_prompt = prompt
    
    latency_ms = (time.time() - start_time) * 1000
    
    return {
        "method": "PromptAgent",
        "original": prompt,
        "refined": refined_prompt,
        "latency_ms": latency_ms,
        "tokens_input": input_tokens,
        "tokens_output": output_tokens,
        "tokens_total": input_tokens + output_tokens
    }

