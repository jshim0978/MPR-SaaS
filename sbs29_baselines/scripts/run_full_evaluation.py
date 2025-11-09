#!/usr/bin/env python3
"""
FULL EVALUATION - Complete Pipeline with All Data Capture
==========================================================
Runs all frameworks on all datasets, capturing:
- Original prompts
- Refined prompts  
- Control outputs (LLM response to original)
- Refined outputs (LLM response to refined)
- All latency and token metrics

For later GPT-5 judge comparison.
"""

import os
import sys
import json
import time
import torch
import wandb
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm

# Add baselines to path
sys.path.insert(0, '/home/comparison/baselines')

from opro_baseline import opro_refine
from promptagent_baseline import promptagent_refine
from promptwizard_baseline import promptwizard_refine
from ape_baseline import ape_refine

# Configuration
MODEL_NAME = "meta-llama/Llama-3.2-3B-Instruct"
CACHE_DIR = "/home/.cache/huggingface"

DECODE_CONFIG = {
    "temperature": 0.2,
    "top_p": 0.9,
    "max_new_tokens": 512,
    "do_sample": True,
    "seed": 13,
}

DATASETS = {
    "truthfulqa": "/home/comparison/datasets/truthfulqa_FULL_817.json",
    "gsm8k": "/home/comparison/datasets/gsm8k_FULL_1319.json",
    "ambigqa": "/home/comparison/datasets/ambigqa_FULL.json",
    "halueval": "/home/comparison/datasets/halueval_SAMPLED_1000.json",  # Sampled for time efficiency
}

FRAMEWORKS = {
    "control": None,
    "opro": opro_refine,
    "promptagent": promptagent_refine,
    "promptwizard": promptwizard_refine,
    # APE skipped per user request for faster completion
}

def load_dataset(dataset_name):
    """Load dataset"""
    path = DATASETS[dataset_name]
    with open(path) as f:
        data = json.load(f)
    
    # Extract prompts
    prompts = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                prompts.append(item)
            elif isinstance(item, dict):
                prompts.append(item.get('question', item.get('prompt', str(item))))
    
    return prompts

def generate_output(prompt, model, tokenizer, device):
    """Generate LLM output for a prompt"""
    start_time = time.time()
    
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    input_tokens = inputs['input_ids'].shape[1]
    
    torch.manual_seed(DECODE_CONFIG['seed'])
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=DECODE_CONFIG['max_new_tokens'],
            temperature=DECODE_CONFIG['temperature'],
            top_p=DECODE_CONFIG['top_p'],
            do_sample=DECODE_CONFIG['do_sample'],
            pad_token_id=tokenizer.eos_token_id
        )
    
    output_tokens = outputs.shape[1] - input_tokens
    output_text = tokenizer.decode(outputs[0][input_tokens:], skip_special_tokens=True).strip()
    
    latency_ms = (time.time() - start_time) * 1000
    
    return {
        "output": output_text,
        "latency_ms": latency_ms,
        "tokens_input": input_tokens,
        "tokens_output": output_tokens,
        "tokens_total": input_tokens + output_tokens
    }

def evaluate_framework_on_dataset(framework_name, dataset_name, model, tokenizer, device, output_dir):
    """Evaluate a framework on a dataset"""
    
    print(f"\n{'='*80}")
    print(f"🚀 EVALUATING: {framework_name.upper()} on {dataset_name.upper()}")
    print(f"{'='*80}")
    
    # Initialize WandB
    wandb.init(
        project="PRaaS-baselines-FULL",
        name=f"{framework_name}-{dataset_name}",
        config={
            "framework": framework_name,
            "dataset": dataset_name,
            "model": MODEL_NAME,
            "temperature": DECODE_CONFIG["temperature"],
            "top_p": DECODE_CONFIG["top_p"],
            "seed": DECODE_CONFIG["seed"],
        },
        reinit=True
    )
    
    # Load dataset
    prompts = load_dataset(dataset_name)
    print(f"   Loaded {len(prompts)} prompts")
    
    # Get framework function
    refine_fn = FRAMEWORKS[framework_name]
    
    results = []
    
    # Cumulative metrics for WandB
    cumulative_refinement_latency = 0
    cumulative_control_latency = 0
    cumulative_refined_latency = 0
    cumulative_total_latency = 0
    cumulative_refinement_tokens = 0
    cumulative_control_tokens = 0
    cumulative_refined_tokens = 0
    cumulative_total_tokens = 0
    
    for idx, original_prompt in enumerate(tqdm(prompts, desc=f"{framework_name}/{dataset_name}")):
        try:
            # Step 1: Refine prompt (or keep original for control)
            if refine_fn is None:
                # Control: no refinement
                refined_prompt = original_prompt
                refinement_result = {
                    "latency_ms": 0,
                    "tokens_input": 0,
                    "tokens_output": 0,
                    "tokens_total": 0
                }
            else:
                # Apply refinement
                refinement_result = refine_fn(original_prompt, model, tokenizer, device)
                refined_prompt = refinement_result['refined']
            
            # Step 2: Generate control output (original prompt → LLM)
            control_gen = generate_output(original_prompt, model, tokenizer, device)
            
            # Step 3: Generate refined output (refined prompt → LLM)
            refined_gen = generate_output(refined_prompt, model, tokenizer, device)
            
            # Compile results
            sample_result = {
                "sample_idx": idx,
                "dataset": dataset_name,
                "framework": framework_name,
                "original_prompt": original_prompt,
                "refined_prompt": refined_prompt,
                "control_output": control_gen['output'],
                "refined_output": refined_gen['output'],
                "refinement_latency_ms": refinement_result['latency_ms'],
                "refinement_tokens": {
                    "input": refinement_result['tokens_input'],
                    "output": refinement_result['tokens_output'],
                    "total": refinement_result['tokens_total']
                },
                "control_generation_latency_ms": control_gen['latency_ms'],
                "control_generation_tokens": {
                    "input": control_gen['tokens_input'],
                    "output": control_gen['tokens_output'],
                    "total": control_gen['tokens_total']
                },
                "refined_generation_latency_ms": refined_gen['latency_ms'],
                "refined_generation_tokens": {
                    "input": refined_gen['tokens_input'],
                    "output": refined_gen['tokens_output'],
                    "total": refined_gen['tokens_total']
                },
                "total_latency_ms": refinement_result['latency_ms'] + control_gen['latency_ms'] + refined_gen['latency_ms'],
                "total_tokens": refinement_result['tokens_total'] + control_gen['tokens_total'] + refined_gen['tokens_total']
            }
            
            results.append(sample_result)
            
            # Update cumulative metrics
            cumulative_refinement_latency += sample_result['refinement_latency_ms']
            cumulative_control_latency += sample_result['control_generation_latency_ms']
            cumulative_refined_latency += sample_result['refined_generation_latency_ms']
            cumulative_total_latency += sample_result['total_latency_ms']
            cumulative_refinement_tokens += sample_result['refinement_tokens']['total']
            cumulative_control_tokens += sample_result['control_generation_tokens']['total']
            cumulative_refined_tokens += sample_result['refined_generation_tokens']['total']
            cumulative_total_tokens += sample_result['total_tokens']
            
            # Log to WandB every 10 samples
            if (idx + 1) % 10 == 0:
                n_samples = idx + 1
                wandb.log({
                    "sample_idx": idx,
                    "samples_completed": n_samples,
                    "avg_refinement_latency_ms": cumulative_refinement_latency / n_samples,
                    "avg_control_latency_ms": cumulative_control_latency / n_samples,
                    "avg_refined_latency_ms": cumulative_refined_latency / n_samples,
                    "avg_total_latency_ms": cumulative_total_latency / n_samples,
                    "avg_refinement_tokens": cumulative_refinement_tokens / n_samples,
                    "avg_control_tokens": cumulative_control_tokens / n_samples,
                    "avg_refined_tokens": cumulative_refined_tokens / n_samples,
                    "avg_total_tokens": cumulative_total_tokens / n_samples,
                })
            
            # Save incrementally every 100 samples
            if (idx + 1) % 100 == 0:
                output_file = output_dir / f"{framework_name}_{dataset_name}_COMPLETE.json"
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=2)
        
        except Exception as e:
            print(f"   ⚠️ Error on sample {idx}: {e}")
            continue
    
    # Save final results
    output_file = output_dir / f"{framework_name}_{dataset_name}_COMPLETE.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"   ✅ Completed: {len(results)}/{len(prompts)} samples")
    print(f"   💾 Saved to: {output_file}")
    
    # Final WandB summary
    n_samples = len(results)
    if n_samples > 0:
        wandb.summary.update({
            "total_samples": n_samples,
            "final_avg_refinement_latency_ms": cumulative_refinement_latency / n_samples,
            "final_avg_control_latency_ms": cumulative_control_latency / n_samples,
            "final_avg_refined_latency_ms": cumulative_refined_latency / n_samples,
            "final_avg_total_latency_ms": cumulative_total_latency / n_samples,
            "final_avg_refinement_tokens": cumulative_refinement_tokens / n_samples,
            "final_avg_control_tokens": cumulative_control_tokens / n_samples,
            "final_avg_refined_tokens": cumulative_refined_tokens / n_samples,
            "final_avg_total_tokens": cumulative_total_tokens / n_samples,
        })
    
    wandb.finish()
    
    return results

def run_gpu_worker(gpu_id, frameworks, datasets):
    """Run evaluation for assigned frameworks on a GPU"""
    
    # Device is always cuda:0 because CUDA_VISIBLE_DEVICES remaps it
    device = "cuda:0"
    
    print(f"\n{'='*80}")
    print(f"🎮 GPU {gpu_id} WORKER STARTING")
    print(f"{'='*80}")
    print(f"Frameworks: {', '.join(frameworks)}")
    print(f"Datasets: {', '.join(datasets)}")
    
    # Load model
    print(f"\n📦 Loading model on GPU {gpu_id}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        cache_dir=CACHE_DIR,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True
    ).to(device)
    model.eval()
    print(f"✅ Model loaded on GPU {gpu_id}")
    
    # Output directory
    output_dir = Path("/home/comparison/results_complete")
    output_dir.mkdir(exist_ok=True)
    
    # Run evaluations
    for framework in frameworks:
        for dataset in datasets:
            evaluate_framework_on_dataset(framework, dataset, model, tokenizer, device, output_dir)
    
    # Cleanup
    del model
    del tokenizer
    torch.cuda.empty_cache()
    
    print(f"\n✅ GPU {gpu_id} WORKER COMPLETED!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--gpu', type=int, required=True, help='GPU ID')
    parser.add_argument('--frameworks', nargs='+', required=True, help='Framework names')
    parser.add_argument('--datasets', nargs='+', required=True, help='Dataset names')
    
    args = parser.parse_args()
    
    run_gpu_worker(args.gpu, args.frameworks, args.datasets)

