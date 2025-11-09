#!/usr/bin/env python3
"""
PromptWizard Baseline
=====================

Paper: Agarwal et al., 2024 - "PromptWizard: Task-Aware Agent-driven Prompt Optimization Framework"
Repo: https://github.com/microsoft/PromptWizard

Synchronized with jw1's configuration:
- Model: Llama-3.2-3B-Instruct
- Temperature: 0.2, Top-p: 0.9, Seed: 13
"""

import time
import torch
import random
from typing import Dict, Any

def promptwizard_refine(prompt: str, model, tokenizer, device=None) -> Dict[str, Any]:
    """
    PromptWizard: Task-aware agent-driven prompt optimization.
    
    Algorithm:
    1. Generate prompt variations via mutation
    2. Critique each variation
    3. Synthesize best elements into final prompt
    
    Simplified to 3 mutation rounds for fair comparison.
    """
    start_time = time.time()
    
    # Use provided device or model's device
    if device is None:
        device = model.device
    
    # Set seeds for reproducibility
    random.seed(13)
    torch.manual_seed(13)
    
    total_input_tokens = 0
    total_output_tokens = 0
    
    # Step 1: Generate 3 variations via mutation
    variations = []
    mutation_operators = [
        "Make this prompt more specific and detailed",
        "Rephrase this prompt to be more structured and clear",
        "Improve this prompt by adding relevant context"
    ]
    
    for operator in mutation_operators:
        mutation_prompt = f"""{operator}: {prompt}

Improved version:"""
        
        # Tokenize
        inputs = tokenizer(mutation_prompt, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        total_input_tokens += inputs['input_ids'].shape[1]
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.2,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        output_tokens = outputs.shape[1] - inputs['input_ids'].shape[1]
        total_output_tokens += output_tokens
        
        # Decode
        raw_variation = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True).strip()
        
        # Parse variation (take first line or first sentence)
        if "Improved version:" in raw_variation:
            variation = raw_variation.split("Improved version:")[-1].strip()
        else:
            # Take the first non-empty line
            lines = [line.strip() for line in raw_variation.split('\n') if line.strip()]
            variation = lines[0] if lines else ""
        
        # Remove trailing explanations
        for stop_marker in ['\n\nChanges', '\n\nThis', '\n\nNote:', '\nExplanation', '\nNote:', '\n\n**']:
            if stop_marker in variation:
                variation = variation.split(stop_marker)[0].strip()
        
        # Cap at reasonable length (2.5x original prompt)
        max_len = min(len(prompt) * 2.5, 300)
        if len(variation) > max_len:
            # Try to cut at a sentence boundary
            sentences = variation.split('. ')
            variation = sentences[0] + '.' if sentences[0] and not sentences[0].endswith('.') else sentences[0]
        
        # Only accept if valid length
        if 10 <= len(variation) <= 500:
            variations.append(variation)
    
    # Step 2: Critique and select best variation
    # For simplicity, use the first valid variation
    # In full PromptWizard, this would involve evaluation on a validation set
    if variations:
        best_variation = variations[0]
    else:
        best_variation = prompt
    
    # Step 3: Synthesize final prompt (simplified - just use best variation)
    refined_prompt = best_variation
    
    latency_ms = (time.time() - start_time) * 1000
    
    return {
        "method": "PromptWizard",
        "original": prompt,
        "refined": refined_prompt,
        "latency_ms": latency_ms,
        "tokens_input": total_input_tokens,
        "tokens_output": total_output_tokens,
        "tokens_total": total_input_tokens + total_output_tokens,
        "mutation_rounds": len(mutation_operators),
        "variations_generated": len(variations)
    }

